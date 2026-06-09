# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    user_id = fields.Many2one(
        "res.users",
        store=True,
        readonly=False,
    )

