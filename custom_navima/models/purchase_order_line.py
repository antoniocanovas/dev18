# Copyright 2024 Punt Sistemes SL

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    pnt_sale_type_id = fields.Many2one(
        related="sale_line_id.order_id.type_id", string="Sale Type", readonly=True
    )
