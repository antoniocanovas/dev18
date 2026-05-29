# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models
from odoo.tools.image import is_image_size_above


class ShoesSku(models.Model):
    _inherit = 'shoes.sku'

    # Aliases needed so shoes.sku can be used as a carousel item in website_sale templates
    image_1920 = fields.Image(related='image')
    can_image_1024_be_zoomed = fields.Boolean(compute='_compute_can_image_1024_be_zoomed', store=True)

    @api.depends('image', 'image_1024')
    def _compute_can_image_1024_be_zoomed(self):
        for sku in self:
            sku.can_image_1024_be_zoomed = (
                bool(sku.image) and is_image_size_above(sku.image, sku.image_1024)
            )
