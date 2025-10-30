# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    pnt_gestor_interno_id = fields.Many2one(
        "res.users",
        string="Gestor Interno",
        compute="_compute_pnt_gestor_interno_id",
        store=True,
        readonly=False,
        help="Responsable del equipo de ventas. Se hereda automáticamente del "
        "equipo de ventas.",
    )

    @api.depends("team_id", "team_id.user_id")
    def _compute_pnt_gestor_interno_id(self):
        for order in self:
            order.pnt_gestor_interno_id = (
                order.team_id.user_id if order.team_id else False
            )
