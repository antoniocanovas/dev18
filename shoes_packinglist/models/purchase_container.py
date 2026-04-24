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

        # --- Lot matching (implemented in Task 5) ---
        return True

    def _process_packing_list_update(self):
        """Split pickings and update container metrics. Implemented in Task 5."""
        raise NotImplementedError("_process_packing_list_update not yet implemented")
