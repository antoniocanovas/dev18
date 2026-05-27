# Copyright 2023 Serincloud SL - Ingenieriacloud.com
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

        sequence = self.company_id.lot_name_sequence
        purchase_all = self.company_id.purchase_all_sale

        # Calcular lotes necesarios por producto (ignorar líneas con PO confirmada)
        needed = {}
        prefix_map = {}
        for li in self.order_line:
            product = li.product_id
            if product.tracking not in ("lot", "serial"):
                continue
            if li.purchase_line_id and li.purchase_line_id.order_id.state in ("purchase", "done"):
                continue
            if purchase_all:
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
            lot_count = quantity if product.tracking == "serial" else 1
            needed[product.id] = needed.get(product.id, 0) + lot_count
            prefix_map.setdefault(product.id, self._build_lot_name_prefix(product))

        # Clasificar lotes existentes: committed (con movimientos) o free
        all_lots = self.env["stock.lot"].search([("sale_id", "=", self.id)])
        if all_lots:
            active_lot_ids = set(
                self.env["stock.move.line"].search([
                    ("lot_id", "in", all_lots.ids),
                    ("state", "not in", ["cancel"]),
                ]).mapped("lot_id").ids
            )
        else:
            active_lot_ids = set()

        committed = {}
        free = {}
        for lot in all_lots:
            pid = lot.product_id.id
            if lot.id in active_lot_ids:
                committed[pid] = committed.get(pid, 0) + 1
            else:
                free.setdefault(pid, self.env["stock.lot"])
                free[pid] |= lot

        # Aplicar delta por producto
        for pid in set(needed) | set(free):
            need = needed.get(pid, 0)
            comm = committed.get(pid, 0)
            free_lots = free.get(pid, self.env["stock.lot"])
            delta = need - comm - len(free_lots)

            if delta > 0:
                prefix = prefix_map.get(pid, "")
                for _ in range(delta):
                    self.env["stock.lot"].create({
                        "name": prefix + sequence.next_by_id(),
                        "product_id": pid,
                        "ref": self.name,
                        "company_id": self.company_id.id,
                        "sale_id": self.id,
                    })
            elif delta < 0:
                free_lots[max(0, need - comm):].unlink()

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

    def _get_matrix(self, product_template):
        matrix = super()._get_matrix(product_template)
        assortment_attr = self.env.company.assortment_attribute_id
        if not assortment_attr:
            return matrix
        custom_ptav_ids = set(self.env["product.template.attribute.value"].search([
            ("product_tmpl_id", "=", product_template.id),
            ("attribute_id", "=", assortment_attr.id),
            ("product_attribute_value_id.assortment_id.custom", "=", True),
        ]).ids)
        if not custom_ptav_ids:
            return matrix

        def _is_custom(cell):
            return bool(cell.get("ptav_ids") and custom_ptav_ids.intersection(cell["ptav_ids"]))

        orig_header = matrix["header"]
        orig_rows = matrix["matrix"]

        # Column indices that have at least one non-custom cell
        valid_cols = {
            col_idx
            for row in orig_rows
            for col_idx, cell in enumerate(row[1:], 1)
            if not _is_custom(cell) and cell.get("ptav_ids")
        }

        matrix["header"] = [orig_header[0]] + [
            orig_header[i] for i in sorted(valid_cols) if i < len(orig_header)
        ]
        matrix["matrix"] = [
            new_row
            for row in orig_rows
            for new_row in [[row[0]] + [row[i] for i in sorted(valid_cols) if i < len(row)]]
            if any(not _is_custom(cell) for cell in new_row[1:])
        ]
        return matrix

    # -------------------------------------------------------------------------
    # Assortment matrix helpers
    # -------------------------------------------------------------------------

    def _find_or_create_shoes_assortment(self, size_qtys):
        ShoesAssortment = self.env["shoes.assortment"]
        for assortment in ShoesAssortment.search([("custom", "=", True)]):
            lines = {line.value_id.id: int(line.quantity) for line in assortment.line_ids}
            if lines == {sid: int(qty) for sid, qty in size_qtys.items()}:
                return assortment
        SizeValue = self.env["product.attribute.value"]
        parts = sorted(
            "%sx%d" % (SizeValue.browse(sid).name, int(qty))
            for sid, qty in size_qtys.items()
        )
        name_code = "+".join(parts)
        return ShoesAssortment.create({
            "name": name_code,
            "code": name_code[:20],
            "custom": True,
            "gender": False,
            "attribute_id": self.env.company.size_attribute_id.id,
            "line_ids": [
                (0, 0, {"value_id": sid, "quantity": int(qty)})
                for sid, qty in size_qtys.items()
            ],
        })

    def _get_or_create_assortment_attribute_value(self, assortment):
        assortment_attribute = self.env.company.assortment_attribute_id
        existing = self.env["product.attribute.value"].search([
            ("assortment_id", "=", assortment.id),
            ("attribute_id", "=", assortment_attribute.id),
        ], limit=1)
        if existing:
            return existing
        return self.env["product.attribute.value"].create({
            "name": assortment.name,
            "attribute_id": assortment_attribute.id,
            "assortment_id": assortment.id,
        })

    def _ensure_assortment_value_on_product(self, assortment_tmpl, assortment_value):
        assortment_attribute = self.env.company.assortment_attribute_id
        ptal = self.env["product.template.attribute.line"].search([
            ("product_tmpl_id", "=", assortment_tmpl.id),
            ("attribute_id", "=", assortment_attribute.id),
        ], limit=1)
        if not ptal:
            self.env["product.template.attribute.line"].create({
                "product_tmpl_id": assortment_tmpl.id,
                "attribute_id": assortment_attribute.id,
                "value_ids": [(4, assortment_value.id)],
            })
        elif assortment_value.id not in ptal.value_ids.ids:
            ptal.write({"value_ids": [(4, assortment_value.id)]})

    def _find_assortment_variant(self, assortment_tmpl, color_value, assortment_value):
        return self.env["product.product"].search([
            ("product_tmpl_id", "=", assortment_tmpl.id),
            ("color_value_id", "=", color_value.id),
            ("assortment_attribute_id", "=", assortment_value.id),
        ], limit=1)

    def _create_assortment_sol(self, order, assortment_variant, qty):
        self.env["sale.order.line"].create({
            "order_id": order.id,
            "product_id": assortment_variant.id,
            "product_uom_qty": qty,
            "price_unit": assortment_variant.lst_price,
        })

    def _apply_specific_mode(self, order, assortment_tmpl, color_value,
                             size_qtys, assortment_qty_boxes):
        assortment = self._find_or_create_shoes_assortment(size_qtys)
        av = self._get_or_create_assortment_attribute_value(assortment)
        self._ensure_assortment_value_on_product(assortment_tmpl, av)
        variant = self._find_assortment_variant(assortment_tmpl, color_value, av)
        if not variant:
            raise UserError(
                _("No se pudo crear la variante del surtido para color %s.")
                % color_value.name
            )
        self._create_assortment_sol(order, variant, assortment_qty_boxes)

    def _apply_auto_mode(self, order, assortment_tmpl, color_value,
                         size_qtys, pairs_qty):
        if not pairs_qty:
            raise UserError(
                _("No se puede distribuir automáticamente: el surtido no tiene pares por caja definidos.")
            )
        assortments_to_apply = []
        remainders = {}
        for size_id, total_qty in size_qtys.items():
            pure_count = int(total_qty // pairs_qty)
            remainder = total_qty % pairs_qty
            if pure_count > 0:
                assortments_to_apply.append(({size_id: pairs_qty}, pure_count))
            if remainder > 0:
                remainders[size_id] = remainder
        for box_qtys in self._pack_remainders(remainders, pairs_qty):
            assortments_to_apply.append((box_qtys, 1))
        for box_size_qtys, box_count in assortments_to_apply:
            assortment = self._find_or_create_shoes_assortment(box_size_qtys)
            av = self._get_or_create_assortment_attribute_value(assortment)
            self._ensure_assortment_value_on_product(assortment_tmpl, av)
            variant = self._find_assortment_variant(assortment_tmpl, color_value, av)
            if variant:
                self._create_assortment_sol(order, variant, box_count)

    def _pack_remainders(self, remainders, max_pairs):
        if not remainders:
            return []
        boxes = []
        current_box = {}
        current_total = 0
        for size_id, qty in sorted(remainders.items(), key=lambda x: x[1], reverse=True):
            remaining = qty
            while remaining > 0:
                space = max_pairs - current_total
                take = min(remaining, space)
                current_box[size_id] = current_box.get(size_id, 0) + take
                current_total += take
                remaining -= take
                if current_total >= max_pairs:
                    boxes.append(dict(current_box))
                    current_box = {}
                    current_total = 0
        if current_box:
            boxes.append(current_box)
        return boxes

    @api.model
    def process_pair_assortment_matrix(self, order_id, product_template_id,
                                        compute_mode, pairs_qty, color_data):
        """
        Called from the ProductMatrixDialog JS when compute_mode is 'specific' or 'auto'.
        color_data: list of {
            'assortment_qty': int,          # only used in 'specific' mode
            'cells': [{'ptav_ids': [int, ...], 'qty': float}, ...]
        }
        Each cell's ptav_ids includes all PTAVs for that variant (color + size).
        Python identifies color vs size via company attribute config.
        """
        order = self.env["sale.order"].browse(order_id)
        color_attribute = self.env.company.color_attribute_id
        size_attribute = self.env.company.size_attribute_id

        pair_tmpl = self.env["product.template"].browse(product_template_id)
        assortment_tmpl = pair_tmpl.product_tmpl_set_id
        if not assortment_tmpl:
            raise UserError(_("El producto no tiene producto surtido (set) asociado."))

        processed_rows = []
        for row in color_data:
            color_value = None
            size_qtys = {}

            for cell in row.get("cells", []):
                qty = cell.get("qty", 0)
                if not qty:
                    continue
                ptavs = self.env["product.template.attribute.value"].browse(
                    cell.get("ptav_ids", [])
                )
                for ptav in ptavs:
                    if ptav.attribute_id == color_attribute:
                        if not color_value:
                            color_value = ptav.product_attribute_value_id
                    elif ptav.attribute_id == size_attribute:
                        sid = ptav.product_attribute_value_id.id
                        size_qtys[sid] = size_qtys.get(sid, 0) + qty

            if not color_value or not size_qtys:
                continue

            processed_rows.append({
                "color_value": color_value,
                "size_qtys": size_qtys,
                "assortment_qty": row.get("assortment_qty", 1),
            })

        if compute_mode == "specific":
            errors = []
            for row in processed_rows:
                total = sum(row["size_qtys"].values())
                boxes = row["assortment_qty"]
                if boxes < 1:
                    errors.append(
                        _("Color %s: el número de surtidos debe ser al menos 1.")
                        % row["color_value"].name
                    )
                elif total > pairs_qty * boxes:
                    errors.append(
                        _("Color %s: %d pares no caben en %d surtido(s) de %d pares.")
                        % (row["color_value"].name, total, boxes, pairs_qty)
                    )
            if errors:
                raise UserError("\n".join(errors))

        for row in processed_rows:
            if compute_mode == "specific":
                self._apply_specific_mode(
                    order, assortment_tmpl, row["color_value"],
                    row["size_qtys"], row["assortment_qty"],
                )
            else:
                self._apply_auto_mode(
                    order, assortment_tmpl, row["color_value"],
                    row["size_qtys"], pairs_qty,
                )

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
        if self.company_id.purchase_all_sale:
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
                    purchase_line = self.env["purchase.order.line"].create(pol_vals)
                    # Indicar en SOL para que no vuelva a crear el pedido:
                    li["purchase_line_id"] = purchase_line.id
