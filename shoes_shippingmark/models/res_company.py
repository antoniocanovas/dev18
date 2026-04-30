# Copyright 2024 Punt Sistemes SL

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    default_shippingmark_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Shipping Mark",
        help="Default shipping mark assigned to the sale_type field when creating a new company partner.",
    )
