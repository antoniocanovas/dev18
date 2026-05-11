# Copyright 2023 Serincloud SL - Ingenieriacloud.com
from typing import Any

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Comercialmente en cada pedido quieren saber cuántos pares se han vendido:
    def _get_shoes_pair_count(self):
        for record in self:
            record["pairs_count"] = sum(li.pairs_count for li in record.order_line)

    pairs_count = fields.Integer(
        string="Pairs", store=False, compute="_get_shoes_pair_count"
    )

    shoes_campaign_id = fields.Many2one(
        "project.project", string="Campaign", store=True, copy=True, tracking=10
    )

    date_cancellation_limit = fields.Date("Cancellation limit")

    shoes_delivery_date_from = fields.Datetime(
        string="Delivery from",
        copy=True,
    )

    @api.depends("shoes_campaign_id")
    def _get_campaign_top_sale(self):
        for record in self:
            models = self.env["product.template"].search(
                [
                    ("shoes_campaign_id", "=", record.shoes_campaign_id.id),
                    ("pairs_sold", ">", 1),
                ],
                limit=10,
            )
            record["campaign_top_ids"] = [(6, 0, models.ids)]

    campaign_top_ids = fields.Many2many(
        "product.template", store=False, compute="_get_campaign_top_sale"
    )

    # Habilita o deshabilita la vista de pares más vendidos en las preferencias
    # de usuario o desde botón en ventas:
    def _get_enabled_top_sales(self):
        self.top_sales = self.env.user.top_sales

    top_sales = fields.Boolean(
        "Top sales", store=False, compute="_get_enabled_top_sales"
    )

    def show_hide_top_sales(self):
        user = self.env.user
        user.top_sales = not user.top_sales

    def _prepare_picking(self):
        res = super()._prepare_picking()
        res["shoes_delivery_date_from"] = self.shoes_delivery_date_from
        return res

    def _delete_unused_lots(self):
        lots = self.env["stock.lot"].search([("sale_id", "=", self.id)])
        safe_to_delete = lots.filtered(
            lambda l: not self.env["stock.move.line"].search_count(
                [("lot_id", "=", l.id), ("state", "not in", ["cancel"])]
            )
        )
        safe_to_delete.unlink()

    def _check_lot_name_prefix_data(self, product):
        company = self.company_id
        errors = []
        if company.lot_name_campaign and not self.shoes_campaign_id:
            errors.append(_("Campaign: el pedido no tiene campaña asignada."))
        if company.lot_name_manufacturer:
            if not product.manufacturer_id:
                errors.append(_(
                    "Manufacturer ref: el producto '%s' no tiene fabricante asignado.",
                    product.display_name,
                ))
            elif not product.manufacturer_id.ref:
                errors.append(_(
                    "Manufacturer ref: el fabricante '%s' no tiene referencia (Ref) definida.",
                    product.manufacturer_id.name,
                ))
        if company.lot_name_brand:
            if not product.product_brand_id:
                errors.append(_(
                    "Brand code: el producto '%s' no tiene marca asignada.",
                    product.display_name,
                ))
            elif not product.product_brand_id.code:
                errors.append(_(
                    "Brand code: la marca '%s' no tiene código (Code) definido.",
                    product.product_brand_id.name,
                ))
        if errors:
            raise UserError(
                _("La configuración de nombre de lote requiere los siguientes datos:\n\n%s")
                % "\n".join("• %s" % e for e in errors)
            )

    def _build_lot_name_prefix(self, product):
        company = self.company_id
        parts = []
        if company.lot_name_campaign and self.shoes_campaign_id:
            parts.append(self.shoes_campaign_id.name or "")
        if company.lot_name_manufacturer and product.manufacturer_id:
            parts.append(product.manufacturer_id.ref or "")
        if company.lot_name_brand and product.product_brand_id:
            parts.append(product.product_brand_id.code or "")
        return "".join(parts)

    def create_lots_for_sale_order(self):
        self.ensure_one()
        if self.env.context.get("skip_lot_creation"):
            return
        if not (self.id and self.order_line and self.state == "sale"):
            return

        self._delete_unused_lots()

        base_name = self.name

        purchase_all = self.company_id.purchase_all_sale
        serial_counter = 1
        for li in self.order_line:
            product = li.product_id
            if product.tracking not in ("lot", "serial"):
                continue
            if purchase_all or li.product_custom_attribute_value_ids:
                quantity = int(li.product_uom_qty)
            elif li.purchase_line_id:
                quantity = int(li.purchase_line_id.product_qty)
            else:
                continue
            if li.purchase_line_id:
                quantity = min(quantity, int(li.purchase_line_id.product_qty))
            if quantity < 1:
                continue

            self._check_lot_name_prefix_data(product)
            prefix = self._build_lot_name_prefix(product)

            if product.tracking == "serial":
                for _ in range(quantity):
                    final_name = prefix + "%s-%03d" % (base_name, serial_counter)
                    existing = self.env["stock.lot"].search(
                        [
                            ("product_id", "=", product.id),
                            ("name", "=", final_name),
                            ("company_id", "=", self.company_id.id),
                        ],
                        limit=1,
                    )
                    if not existing:
                        self.env["stock.lot"].create(
                            {
                                "name": final_name,
                                "product_id": product.id,
                                "ref": self.name,
                                "company_id": self.company_id.id,
                                "sale_id": self.id,
                            }
                        )
                    serial_counter += 1
            else:
                final_name = prefix + base_name
                existing = self.env["stock.lot"].search(
                    [
                        ("product_id", "=", product.id),
                        ("name", "=", final_name),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
                if not existing:
                    self.env["stock.lot"].create(
                        {
                            "name": final_name,
                            "product_id": product.id,
                            "ref": self.name,
                            "company_id": self.company_id.id,
                            "sale_id": self.id,
                        }
                    )

    def _action_confirm(self):
        # skip_lot_creation: la automación dispara durante el super() cuando state='sale',
        # pero en ese momento purchase_line_id aún no existe (se crea a continuación).
        # Suprimimos la automación aquí y llamamos create_lots_for_sale_order() nosotros
        # después de crear los PO lines, para que el purchase_line_id ya esté disponible.
        result = super(SaleOrder, self.with_context(skip_lot_creation=True))._action_confirm()
        self.create_purchase_lines_for_custom_products()
        for order in self.filtered(lambda o: o.state == "sale"):
            order.create_lots_for_sale_order()
        return result

    def _get_qty_to_purchase(self, sol, qty_sold=None):
        """
        Return the net quantity to purchase for a sale order line.

        qty_sold: override the sold quantity (used when called before the SOL write
                  so product_uom_qty still holds the old value).

        When purchase_all_sale is True (default): returns the full sold qty.
        When False: uses stock available (free + reserved for this SO) and free
        incoming to compute the net quantity that still needs to be bought.
        """
        if qty_sold is None:
            qty_sold = sol.product_uom_qty
        if self.company_id.purchase_all_sale or sol.product_custom_attribute_value_ids:
            return qty_sold

        # --- Stock available from inventory ---
        # Use quants to get physically available stock, filtered by shippingmark
        # when the customer has exclusive marks.
        quants = self.env["stock.quant"].search(
            [
                ("product_id", "=", sol.product_id.id),
                ("location_id.usage", "=", "internal"),
            ]
        )
        partner = sol.order_id.partner_id
        exclusive_marks = partner.shoes_shippingmark_ids
        if exclusive_marks and sol.product_id.is_assortment:
            allowed_ids = exclusive_marks.ids
            quants = quants.filtered(
                lambda q: q.lot_id
                and q.lot_id.shippingmark_id.id in allowed_ids
            )

        # Unreserved stock (free for anyone)
        free_stock = sum(
            max(0.0, q.quantity - q.reserved_quantity) for q in quants
        )
        # Stock already reserved for THIS sale order's outgoing moves
        # (compatible with shippingmarks since Odoo applied the filter on assign)
        delivery_moves = self.env["stock.move"].search(
            [
                ("sale_line_id", "=", sol.id),
                ("state", "not in", ["done", "cancel"]),
                ("picking_type_id.code", "=", "outgoing"),
            ]
        )
        reserved_for_this_so = sum(
            sum(ml.quantity for ml in m.move_line_ids
                if ml.state not in ("done", "cancel"))
            for m in delivery_moves
        )
        available = free_stock + reserved_for_this_so

        # --- Free incoming: pending receipts not committed to any sale order ---
        free_incoming_moves = self.env["stock.move"].search(
            [
                ("product_id", "=", sol.product_id.id),
                (
                    "state",
                    "in",
                    ["assigned", "waiting", "confirmed", "partially_available"],
                ),
                ("picking_type_id.code", "=", "incoming"),
                ("purchase_line_id.sale_line_id", "=", False),
            ]
        )
        free_incoming = sum(free_incoming_moves.mapped("product_qty"))

        return max(0.0, qty_sold - available - free_incoming)

    def create_purchase_lines_for_custom_products(self):
        for record in self:
            for li in record.order_line:
                # Bug líneas de compra duplicadas:
                if li.product_id.is_assortment and not li.purchase_line_id:
                    vendor = li.product_id.manufacturer_id
                    if not vendor:
                        raise UserError(
                            _(
                                "El producto '%s' no tiene fabricante asignado. "
                                "Asígnalo en la ficha del producto antes de confirmar el pedido.",
                                li.product_id.display_name,
                            )
                        )

                    qty_to_buy = record._get_qty_to_purchase(li)
                    if qty_to_buy <= 0:
                        continue

                    # Precio por surtido: exwork × pares por unidad de surtido
                    if li.product_custom_attribute_value_ids:
                        pairs_per_unit = li.custom_assortment_pairs
                    else:
                        pairs_per_unit = li.product_id.pairs_count
                    price_unit = li.product_id.exwork * pairs_per_unit

                    draft_purchases = self.env["purchase.order"].search(
                        [("partner_id", "=", vendor.id), ("state", "=", "draft")]
                    )
                    po = draft_purchases[0] if draft_purchases.ids else self.env[
                        "purchase.order"
                    ].create({"partner_id": vendor.id})

                    pol_vals = {
                        "order_id": po.id,
                        "product_id": li.product_id.id,
                        "sale_line_id": li.id,
                        "name": li.name,
                        "price_unit": price_unit,
                        "product_qty": qty_to_buy,
                    }
                    if li.product_custom_attribute_value_ids:
                        pol_vals["assortment_pair_id"] = (
                            li.product_custom_attribute_value_ids[0].id
                        )

                    purchase_line = self.env["purchase.order.line"].create(pol_vals)
                    # Indicar en SOL para que no vuelva a crear el pedido:
                    li["purchase_line_id"] = purchase_line.id
