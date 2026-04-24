from odoo import _, fields, models
from odoo.exceptions import UserError


class ContainerValidateWizard(models.TransientModel):
    _name = "container.validate.wizard"
    _description = "Validate Container Pickings"

    container_id = fields.Many2one("purchase.container", readonly=True, required=True)
    location_dest_id = fields.Many2one(
        "stock.location",
        string="Destination Location",
        required=True,
        domain=[("usage", "in", ["internal", "transit"])],
    )

    def action_validate(self):
        self.ensure_one()
        pickings = self.container_id.picking_ids.filtered(
            lambda p: p.state not in ("done", "cancel")
        )
        if not pickings:
            raise UserError(_("No hay albaranes pendientes en este contenedor."))

        for picking in pickings:
            picking.location_dest_id = self.location_dest_id
            picking.move_ids.write({"location_dest_id": self.location_dest_id.id})
            picking.move_line_ids.filtered(
                lambda ml: ml.state not in ("done", "cancel")
            ).write({"location_dest_id": self.location_dest_id.id})

        for picking in pickings:
            picking.with_context(skip_backorder=True).button_validate()

        return {"type": "ir.actions.act_window_close"}
