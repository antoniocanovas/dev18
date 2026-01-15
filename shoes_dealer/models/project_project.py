# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProjectProject(models.Model):
    _inherit = "project.project"

    # Cambio de moneda estimado para cálculo de precios de pares y surtidos
    # en base a exwork:
    dollar_exchange = fields.Float(
        "Exchange € => cc",
        store=True,
        copy=False,
        default=1,
        help="Exchange from € to campaign currency.",
    )
    # Secuencia del jefe para encontrar rápido los productos, es por campaña
    # y numérica ordenada:
    campaign_code = fields.Integer("Next code", store=True, copy=False, default=1)
    default_sale_margin = fields.Float(
        string="Default Sale Margin",
        help="Margin percentage applied to new products in this campaign.",
        default=0.0,
    )

    @api.constrains("dollar_exchange")
    def _get_dollar_exchange_not_null(self):
        if self.dollar_exchange == 0:
            raise UserError("El cambio de moneda no puede ser nulo.")
