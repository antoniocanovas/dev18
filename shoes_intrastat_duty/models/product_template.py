# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    estimated_pair_landed_cost = fields.Monetary(
        "Pair landed cost €",
        help="Estimated pair landed cost, based on intrastat duty.",
        compute="_get_estimated_pair_landed_cost",
    )

    # Calcula el valor de estimated_pair_landed_cost basado en la moneda y duty
    # estimation:
    @api.onchange("exwork_single")
    def _get_estimated_pair_landed_cost(self):
        for record in self:
            amount = 0
            duty_percent = (
                record.intrastat_duty_id.duty if record.intrastat_duty_id else 0.0
            )
            if record.is_assortment:
                amount = record.exwork_single_euro * (1 + duty_percent / 100)
            if record.is_pair:
                amount = record.exwork_euro * (1 + duty_percent / 100)
            record.estimated_pair_landed_cost = amount

    @api.depends("exwork", "sale_margin")
    def _compute_recommended_sale_price(self):
        super()._compute_recommended_sale_price()
        for product in self:
            duty_percent = (
                product.intrastat_duty_id.duty if product.intrastat_duty_id else 0.0
            )
            duty_amount = (product.exwork or 0.0) * duty_percent / 100
            product.recommended_sale_price += duty_amount
