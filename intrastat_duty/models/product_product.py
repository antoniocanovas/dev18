# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    estimated_landed_cost = fields.Float(
        string="Estimated landed cost",
        compute="_compute_estimated_landed_cost",
        store=True,
        digits="Product Price",
        help="Estimated cost including duties (standard_price * (1 + duty/100))",
    )

    @api.depends("standard_price", "product_tmpl_id.intrastat_duty_id.duty")
    def _compute_estimated_landed_cost(self):
        for product in self:
            duty_percent = (
                product.product_tmpl_id.intrastat_duty_id.duty
                if product.product_tmpl_id.intrastat_duty_id
                else 0.0
            )
            product.estimated_landed_cost = product.standard_price * (
                1 + duty_percent / 100
            )
