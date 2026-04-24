from odoo import fields, models


class PurchaseContainer(models.Model):
    _inherit = "purchase.container"

    container_line_ids = fields.One2many(
        "purchase.container.line",
        "container_id",
        string="Packing List",
        copy=False,
    )
