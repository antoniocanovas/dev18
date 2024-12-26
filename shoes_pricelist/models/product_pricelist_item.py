# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductPricelistItem(models.Model):
    _inherit = ["product.pricelist.item"]


    shoes_campaign_id = fields.Many2one("project.project", string="Campaign",
                                        related='product_tmpl_id.shoes_campaign_id')
