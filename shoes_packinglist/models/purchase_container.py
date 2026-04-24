from odoo import _, fields, models
from odoo.exceptions import UserError


class PurchaseContainer(models.Model):
    _inherit = "purchase.container"

    container_line_ids = fields.One2many(
        "purchase.container.line",
        "container_id",
        string="Packing List",
        copy=False,
    )

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
        # Reset previous matching
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
            move_line = self.env["stock.move.line"].search(
                [
                    ("lot_id", "=", lot.id),
                    ("picking_id", "in", pending_pickings.ids),
                    ("state", "not in", ["done", "cancel"]),
                ],
                limit=1,
            )
            if move_line:
                line.move_id = move_line.move_id
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
            picking_matched_lines = processed_lines.filtered(
                lambda l: l.move_id.picking_id == picking
            )
            picking_matched_lot_names = set(picking_matched_lines.mapped("lot"))
            all_mls = picking.move_line_ids.filtered(
                lambda ml: ml.state not in ("done", "cancel")
            )
            matched_mls = all_mls.filtered(
                lambda ml: ml.lot_id and ml.lot_id.name in picking_matched_lot_names
            )
            remaining_mls = all_mls - matched_mls

            if not remaining_mls:
                picking.container_id = self.id
            else:
                self._split_picking(picking, remaining_mls)
                picking.container_id = self.id

        # Update container metrics
        self.weight = sum(processed_lines.mapped("assortment_gross_weight"))
        self.volume = sum(processed_lines.mapped("volume"))
        self.package_qty = len(processed_lines)

    def _split_picking(self, picking, remaining_mls):
        """
        Move remaining_mls to a new backorder picking.
        Splits stock.move records when only some of their lines go to the backorder.
        """
        backorder_vals = picking.copy_data(
            default={
                "move_ids": [],
                "move_line_ids": [],
                "backorder_id": picking.id,
            }
        )[0]
        backorder = self.env["stock.picking"].create(backorder_vals)

        # Group remaining move_lines by their parent move
        remaining_by_move = {}
        for ml in remaining_mls:
            remaining_by_move.setdefault(ml.move_id, self.env["stock.move.line"])
            remaining_by_move[ml.move_id] |= ml

        for move, rem_lines in remaining_by_move.items():
            all_move_mls = move.move_line_ids.filtered(
                lambda ml: ml.state not in ("done", "cancel")
            )
            if len(all_move_mls) == len(rem_lines):
                # All lines of this move go to backorder — move the move; lines follow
                move.write({"picking_id": backorder.id})
            else:
                # Partial: create new move in backorder for remaining lines
                remaining_qty = sum(rem_lines.mapped("quantity"))
                new_move = move.copy(
                    default={
                        "picking_id": backorder.id,
                        "product_uom_qty": remaining_qty,
                        "move_line_ids": [],
                    }
                )
                rem_lines.write(
                    {"picking_id": backorder.id, "move_id": new_move.id}
                )
                # Reduce original move qty to matched lines only
                matched_qty = sum((all_move_mls - rem_lines).mapped("quantity"))
                move.product_uom_qty = matched_qty
