# Copyright 2024 Punt Sistemes SL

from odoo import models


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    _sql_constraints = [
        (
            "name_uniq",
            "UNIQUE(name)",
            "A Shipping Mark with this name already exists.",
        ),
    ]
