# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = "project.project"

    # Cambio de moneda estimado para cálculo de precios de pares y surtidos en base a exwork:
    currency_exchange = fields.Float('Currency exchange', store=True, copy=False, default=1)
    # Secuencia del jefe para encontrar rápido los productos, es por campaña y numérica ordenada:
    campaign_code = fields.Integer('Next code', store=True, copy=False, default=1)

    @api.constrains('currency_exchange')
    def _get_currency_exchange_not_null(self):
        if self.currency_exchange == 0:
            raise UserError('El cambio de moneda no puede ser nulo.')