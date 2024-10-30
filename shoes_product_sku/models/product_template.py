# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _update_product_product_sku(self):
        for r in records:

            if r.is_pair:
                for product in r.product_variant_ids:

                    a=1
            elif r.is_assortment:
                for product in r.product_variant_ids:
                    a=1
            else:
                continue
