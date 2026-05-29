# Copyright Serincloud SL - 2025
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    commercial_validation = fields.Selection(
        selection=[
            ("pending", "Pendiente de Aprobación"),
            ("approved", "Aprobado"),
            ("rejected", "Rechazado"),
        ],
        string="Validación Comercial",
        default="pending",
        copy=False,
        tracking=True,
        index=True,
    )

    def action_commercial_approve(self):
        for picking in self:
            picking.commercial_validation = "approved"

    def action_commercial_reject(self):
        for picking in self:
            picking.commercial_validation = "rejected"

    def action_commercial_set_pending(self):
        for picking in self:
            picking.commercial_validation = "pending"

    def button_validate(self):
        # Bloqueo universal: ningún usuario puede validar una salida sin aprobación comercial,
        # independientemente de su rol. El comercial debe aprobar explícitamente antes de que
        # el almacén (o cualquier automatización) pueda despachar la mercancía.
        blocked = self.filtered(
            lambda p: p.picking_type_id.code == "outgoing"
            and p.commercial_validation != "approved"
        )
        if blocked:
            names = ", ".join(blocked.mapped("name"))
            raise UserError(
                _(
                    "Los siguientes albaranes deben ser aprobados comercialmente "
                    "antes de validar la salida:\n%s"
                )
                % names
            )
        return super().button_validate()
