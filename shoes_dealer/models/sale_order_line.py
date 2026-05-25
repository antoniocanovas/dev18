# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    purchase_line_id = fields.Many2one("purchase.order.line", string="Purchase line", copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        orders_to_sync = self.env["sale.order"]
        for line in lines:
            if (
                line.product_id.is_assortment
                and not line.purchase_line_id
                and line.order_id.state in ("sale", "done")
            ):
                line.order_id.create_purchase_lines_for_custom_products()
                orders_to_sync |= line.order_id
        for order in orders_to_sync:
            order.create_lots_for_sale_order()
        return lines

    def unlink(self):
        # Collect confirmed orders before the lines disappear
        orders = self.filtered(
            lambda l: l.order_id.state in ("sale", "done")
        ).mapped("order_id")
        result = super().unlink()
        for order in orders:
            order.create_lots_for_sale_order()
        return result

    def write(self, vals):
        orders_to_sync = self.env["sale.order"]

        if "product_uom_qty" in vals:
            new_qty = vals["product_uom_qty"]
            for line in self:
                if not (
                    line.product_id.is_assortment
                    and line.order_id.state in ("sale", "done")
                    and new_qty != line.product_uom_qty
                ):
                    continue
                pol = line.purchase_line_id
                if pol and pol.order_id.state in ("purchase", "done"):
                    if new_qty > line.product_uom_qty:
                        raise UserError(
                            _(
                                "La compra del producto '%s' ya fue confirmada. "
                                "Para incrementar la cantidad, añade una nueva línea en el presupuesto.\n\n"
                                "Recuerda que para introducir nuevas líneas del mismo producto si el pedido "
                                "está confirmado, el tipo de introducción de líneas ha de ser "
                                "\"Product configurator\", probablemente por defecto tienes \"Matrix Grid\" "
                                "al principio de la nueva línea; también es buena opción hacer un nuevo pedido.",
                                line.product_id.display_name,
                            )
                        )
                    # PO confirmada + decremento → no tocar lotes
                    continue
                if pol and pol.order_id.state != "cancel":
                    qty_for_po = line.order_id._get_qty_to_purchase(line, qty_sold=new_qty)
                    pairs_per_unit = line.product_id.pairs_count
                    pol.with_context(from_sale_order_line=True).write({
                        "product_qty": qty_for_po,
                        "price_unit": line.product_id.exwork * pairs_per_unit,
                    })
                orders_to_sync |= line.order_id

        # skip_lot_creation evita que la acción automática de sale.order dispare
        # create_lots_for_sale_order() durante el super().write() (doble ejecución
        # que borraba lotes recién creados y causaba MissingError en stock.lot)
        result = super(SaleOrderLine, self.with_context(skip_lot_creation=True)).write(vals)

        if "product_uom_qty" in vals:
            self._sync_delivery_move_qty()

        for order in orders_to_sync:
            order.create_lots_for_sale_order()

        return result

    def _sync_delivery_move_qty(self):
        """Actualiza product_uom_qty en los movimientos de entrega pendientes."""
        for line in self.filtered(lambda l: l.order_id.state in ("sale", "done")):
            pending_moves = self.env["stock.move"].search([
                ("sale_line_id", "=", line.id),
                ("state", "not in", ["done", "cancel"]),
                ("picking_type_id.code", "=", "outgoing"),
            ])
            if not pending_moves:
                continue
            target_qty = max(0.0, line.product_uom_qty - line.qty_delivered)
            pending_moves.filtered(
                lambda m: m.product_uom_qty != target_qty
            ).write({"product_uom_qty": target_qty})

    # Comercialmente en cada pedido quieren saber cuántos pares se han vendido:
    @api.depends("product_id", "product_uom_qty")
    def _get_shoes_sale_line_pair_count(self):
        for record in self:
            record.pairs_count = record.product_id.pairs_count * record.product_uom_qty

    pairs_count = fields.Integer(
        "Pairs", store=True, compute="_get_shoes_sale_line_pair_count"
    )

    def _get_pricelist_price(self):
        self.ensure_one()
        self.product_id.ensure_one()

        price = super()._get_pricelist_price()
        return price

    @api.depends("write_date")
    def _get_assortment_pair(self):
        for record in self:
            cleanvalues = ""
            if record.product_id.is_assortment and record.name:
                if record.product_id.bom_ids.ids:
                    bom = record.product_id.bom_ids[0]
                    cleanvalues = bom.assortment_pair
            record["assortment_pair"] = cleanvalues

    assortment_pair = fields.Char("Assortment pairs", compute="_get_assortment_pair")

    # Precio especial del para en la línea de ventas, recalculará precio unitario del
    # producto surtido:
    special_pair_price = fields.Monetary("SPP", help="Special pair price")

    @api.onchange("special_pair_price")
    def _update_price_unit_from_spp(self):
        for record in self:
            if record.product_uom_qty > 0:
                record["price_unit"] = (
                    record.pairs_count
                    * record.special_pair_price
                    / record.product_uom_qty
                )

    # Para informes:
    state_id = fields.Many2one(
        "res.country.state",
        "Customer State",
        readonly=True,
        store=True,
        related="order_partner_id.state_id",
    )

    country_id = fields.Many2one(
        "res.country",
        "Customer Country",
        readonly=True,
        store=True,
        related="order_partner_id.country_id",
    )

    product_tmpl_model_id = fields.Many2one(
        "product.template",
        string="Shoes Model",
        store=True,
        related="product_id.product_tmpl_model_id",
    )
    color_value_id = fields.Many2one(
        "product.attribute.value",
        string="Shoes Color",
        store=True,
        related="product_id.color_value_id",
    )
    shoes_campaign_id = fields.Many2one(
        "project.project",
        string="Shoes Campaign",
        store=True,
        related="order_id.shoes_campaign_id",
    )
    product_brand_id = fields.Many2one(
        "product.brand",
        string="Brand",
        store=True,
        related="product_id.product_brand_id",
    )
    product_tmpl_id = fields.Many2one(
        string="S Model",
        comodel_name="product.template",
        related="product_id.product_tmpl_id",
        store=True,
        help="Used for group views in sale order line",
    )
    manufacturer_id = fields.Many2one(
        string="Manufacturer",
        comodel_name="res.partner",
        related="product_id.manufacturer_id",
        store=True,
        help="Used for group by manufacturer in sale order line views",
    )

    @api.depends("state")
    def _get_quoted_quantity(self):
        for record in self:
            record.qty_quoted = (
                record.product_uom_qty
                if record.state not in ["sale", "done", "cancel"]
                else 0
            )

    qty_quoted = fields.Float(
        "Quoted qty", store=True, copy=False, compute="_get_quoted_quantity"
    )

    # Precio por par según tarifa:
    @api.depends("product_id", "price_unit", "product_uom_qty")
    def _get_shoes_pair_price(self):
        for record in self:
            total = 0
            if record.pairs_count != 0:
                total = record.price_subtotal / record.pairs_count
            record["pair_price"] = total

    pair_price = fields.Float("Pair price", store=True, compute="_get_shoes_pair_price")

    product_saleko_id = fields.Many2one(
        "product.product", string="Product KO", store=True, copy=True
    )

    @api.onchange("product_saleko_id")
    def change_saleproductok_2_saleproductko(self):
        self.product_id = self.product_saleko_id.id

