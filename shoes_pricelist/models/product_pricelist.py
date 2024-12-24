# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    # Función para actualizar tarifasde precio:
    def _update_campaign_pricelist(self):
        return True
