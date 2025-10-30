# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"


    estimated_pair_landed_cost = fields.Monetary(
        "Pair landed cost €",
        help='Estimated pair landed cost, based on intrastat duty.',
        compute="_get_estimated_pair_landed_cost",
    )

    # Calcula el valor de estimated_pair_landed_cost basado en la moneda y duty estimation:
    @api.onchange("exwork_single")
    def _get_estimated_pair_landed_cost(self):
        for record in self:
            amount = 0
            duty_percent = record.intrastat_duty_id.duty if record.intrastat_duty_id else 0.0
            if record.is_assortment:
                amount = record.exwork_single_euro * (1 + duty_percent / 100)
            if record.is_pair:
                amount = record.exwork_euro * (1 + duty_percent / 100)
            record.estimated_pair_landed_cost = amount
