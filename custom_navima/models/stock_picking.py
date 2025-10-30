# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    user_id = fields.Many2one(
        compute="_compute_user_id",
        store=True,
        readonly=False,
    )

    @api.depends("sale_id", "sale_id.pnt_gestor_interno_id")
    def _compute_user_id(self):
        for picking in self:
            # Solo actualizar si el albarán está en estados editables
            if picking.state in ["draft", "waiting", "confirmed"]:
                if picking.sale_id and picking.sale_id.pnt_gestor_interno_id:
                    picking.user_id = picking.sale_id.pnt_gestor_interno_id
