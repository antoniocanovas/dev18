from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseContainer(models.Model):
    _inherit = "purchase.container"

    container_line_ids = fields.One2many(
        "purchase.container.line",
        "container_id",
        string="Packing List",
        copy=False,
    )
    container_line_count = fields.Integer(
        compute="_compute_container_line_count",
        string="Packing List Lines",
    )

    @api.depends("container_line_ids")
    def _compute_container_line_count(self):
        for rec in self:
            rec.container_line_count = len(rec.container_line_ids)

    def action_open_validate_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Validar albaranes"),
            "res_model": "container.validate.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_container_id": self.id},
        }

    def action_view_packing_list(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Packing List"),
            "res_model": "purchase.container.line",
            "view_mode": "list,form",
            "domain": [("container_id", "=", self.id)],
            "context": {"default_container_id": self.id},
        }

    def action_update_from_packing_list(self):
        self.ensure_one()

        # --- Validation ---
        if not self.shipping_agent_id:
            raise UserError(
                _(
                    "Debe definir el agente de transporte (Shipping Agent) "
                    "del contenedor."
                )
            )
        if not self.container_line_ids:
            raise UserError(
                _(
                    "No hay líneas en el packing list. "
                    "Importe las líneas antes de actualizar."
                )
            )
        pending_pickings = self.env["stock.picking"].search(
            [
                ("partner_id", "=", self.shipping_agent_id.id),
                ("picking_type_id.code", "=", "incoming"),
                (
                    "state",
                    "in",
                    ["assigned", "waiting", "confirmed", "partially_available"],
                ),
            ]
        )
        if not pending_pickings:
            raise UserError(
                _('El proveedor "%s" no tiene albaranes de recepción pendientes.')
                % self.shipping_agent_id.name
            )

        # --- Lot matching ---
        # Lots from purchase_lot_preassignment exist as stock.lot records but are not
        # yet assigned to incoming move lines before reception. Match each lot to the
        # stock.move in the pending picking via the lot's product, with a more precise
        # secondary filter through the sale order when lot.ref is available.
        self.container_line_ids.write({"move_id": False})

        unmatched = self.env["purchase.container.line"]
        for line in self.container_line_ids:
            if not line.lot:
                unmatched |= line
                continue
            lot = self.env["stock.lot"].search(
                [
                    ("name", "=", line.lot),
                    ("company_id", "=", self.env.company.id),
                ],
                limit=1,
            )
            if not lot:
                unmatched |= line
                continue
            # Build base domain: product in pending pickings, not done/cancel
            base_domain = [
                ("picking_id", "in", pending_pickings.ids),
                ("product_id", "=", lot.product_id.id),
                ("state", "not in", ["done", "cancel"]),
            ]
            # Prefer match through the sale order chain (lot.ref = SO name)
            # purchase_lot_preassignment sets lot.ref = sale order name
            move = False
            if lot.ref:
                move = self.env["stock.move"].search(
                    base_domain
                    + [("purchase_line_id.sale_line_id.order_id.name", "=", lot.ref)],
                    limit=1,
                )
            if not move:
                move = self.env["stock.move"].search(base_domain, limit=1)
            if move:
                line.move_id = move
            else:
                unmatched |= line

        # --- Open wizard if there are unmatched lines ---
        if unmatched:
            wizard = self.env["packing.list.warning.wizard"].create(
                {
                    "container_id": self.id,
                    "warning_line_ids": [
                        (
                            0,
                            0,
                            {
                                "lot": ln.lot,
                                "name": ln.name,
                                "purchase_order": ln.purchase_order,
                            },
                        )
                        for ln in unmatched
                    ],
                }
            )
            return {
                "type": "ir.actions.act_window",
                "res_model": "packing.list.warning.wizard",
                "res_id": wizard.id,
                "view_mode": "form",
                "target": "new",
            }

        # --- All matched: proceed directly ---
        self._process_packing_list_update()
        return True

    def _process_packing_list_update(self):
        """Split pickings and update container metrics. Called after lot matching."""
        self.ensure_one()
        processed_lines = self.container_line_ids.filtered("move_id")
        if not processed_lines:
            return

        involved_pickings = processed_lines.mapped("move_id.picking_id")

        for picking in involved_pickings:
            matched_moves = processed_lines.filtered(
                lambda l: l.move_id.picking_id == picking
            ).mapped("move_id")
            all_moves = picking.move_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            remaining_moves = all_moves - matched_moves

            if not remaining_moves:
                picking.container_id = self.id
            else:
                self._split_picking(picking, remaining_moves)
                picking.container_id = self.id

        # Assign lots to move lines so the picking can be validated
        self._assign_lots_to_moves(processed_lines)

        # Update container metrics
        self.weight = sum(processed_lines.mapped("assortment_gross_weight"))
        self.volume = sum(processed_lines.mapped("volume"))
        self.package_qty = len(processed_lines)

        # Update product weight/volume data from packing list
        self._update_product_weights_from_packing_list(processed_lines)

    def _assign_lots_to_moves(self, processed_lines):
        """
        Pre-assign lots to stock.move.line records so the picking can be validated.

        purchase_lot_preassignment creates stock.lot records but does not put them
        on move lines before reception. This method creates one move line per
        packing list line with the matched lot and its quantity (pairs).

        Existing no-lot move lines (created by action_assign) are removed first
        to avoid duplicates.
        """
        # Remove generic no-lot move lines from all matched moves
        matched_moves = processed_lines.mapped("move_id")
        for move in matched_moves:
            move.move_line_ids.filtered(
                lambda ml: not ml.lot_id and ml.state not in ("done", "cancel")
            ).unlink()

        # Create one move line per packing list line with the specific lot
        for line in processed_lines:
            lot = self.env["stock.lot"].search(
                [("name", "=", line.lot), ("company_id", "=", self.env.company.id)],
                limit=1,
            )
            if not lot:
                continue
            move = line.move_id
            # Skip if this lot is already on a move line (idempotent re-run)
            if move.move_line_ids.filtered(
                lambda ml: ml.lot_id == lot and ml.state not in ("done", "cancel")
            ):
                continue
            self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": move.picking_id.id,
                    "product_id": lot.product_id.id,
                    "lot_id": lot.id,
                    "quantity": 1.0,
                    "product_uom_id": move.product_uom.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                }
            )

    def _update_product_weights_from_packing_list(self, processed_lines):
        """
        Update weight, net_weight, volume on product templates and width_length_high
        on the assortment product.product. Also writes all four fields to the matched
        stock.lot for each line (no deduplication — each line has its own lot).

        For assortment products: writes assortment_gross_weight, assortment_net_weight,
        volume to product.template; width_length_high to product.product.
        For pair products (linked via product_tmpl_single_id): writes pair_gross_weight,
        pair_net_weight, volume / pairs to product.template only.
        Deduplicates product writes by product.id so each product is written once.
        """
        seen_product_ids = set()
        for line in processed_lines:
            if not line.move_id:
                continue
            product = line.move_id.product_id
            if not product:
                continue

            # Build W×L×H string from dimension fields
            wlh_parts = [line.width, line.length, line.high]
            if any(wlh_parts):
                width_length_high = "×".join(
                    str(int(v) if v == int(v) else v) for v in wlh_parts
                )
            else:
                width_length_high = False

            # Update lot fields (per line, no deduplication)
            lot = self.env["stock.lot"].search(
                [("name", "=", line.lot), ("company_id", "=", self.env.company.id)],
                limit=1,
            )
            if lot:
                lot_vals = {
                    "weight": line.assortment_gross_weight,
                    "net_weight": line.assortment_net_weight,
                    "volume": line.volume,
                }
                if width_length_high:
                    lot_vals["width_length_high"] = width_length_high
                lot.write(lot_vals)

            # Deduplicate product/template writes by product.id
            if product.id in seen_product_ids:
                continue
            seen_product_ids.add(product.id)

            tmpl = product.product_tmpl_id

            # Update assortment template (weight/net_weight/volume)
            assortment_vals = {
                "weight": line.assortment_gross_weight,
                "net_weight": line.assortment_net_weight,
                "volume": line.volume,
            }
            tmpl.write(assortment_vals)

            # Update assortment product.product (width_length_high only)
            if width_length_high:
                product.write({"width_length_high": width_length_high})

            # Update pair products (template only, no width_length_high)
            pair_tmpl = getattr(product, "product_tmpl_single_id", False)
            if not pair_tmpl:
                continue
            pairs = line.pairs or 1.0
            pair_vals = {
                "weight": line.pair_gross_weight,
                "net_weight": line.pair_net_weight,
                "volume": line.volume / pairs,
            }
            pair_tmpl.write(pair_vals)

    def _split_picking(self, picking, remaining_moves):
        """
        Move remaining_moves to a new backorder picking.
        Lots are not yet on move lines at packing list import time, so the split
        operates at the stock.move level (whole moves), not at the move line level.
        """
        backorder_vals = picking.copy_data(
            default={
                "move_ids": [],
                "move_line_ids": [],
                "backorder_id": picking.id,
            }
        )[0]
        backorder = self.env["stock.picking"].create(backorder_vals)

        for move in remaining_moves:
            pending_mls = move.move_line_ids.filtered(
                lambda ml: ml.state not in ("done", "cancel")
            )
            move.write({"picking_id": backorder.id})
            if pending_mls:
                pending_mls.write({"picking_id": backorder.id})
