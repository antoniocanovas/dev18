# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    intrastat_duty_id = fields.Many2one(
        "intrastat.duty", string="Duty estimation", ondelete="restrict"
    )

    estimated_landed_cost = fields.Float(
        string="Estimated landed cost",
        compute="_compute_estimated_landed_cost",
        store=True,
        digits="Product Price",
        help="Estimated cost including duties (standard_price * (1 + duty/100))",
    )

    @api.depends("standard_price", "intrastat_duty_id.duty")
    def _compute_estimated_landed_cost(self):
        for template in self:
            duty_percent = (
                template.intrastat_duty_id.duty if template.intrastat_duty_id else 0.0
            )
            template.estimated_landed_cost = template.standard_price * (
                1 + duty_percent / 100
            )
