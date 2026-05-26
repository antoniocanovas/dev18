# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models


class ProductImage(models.Model):
    _inherit = 'product.image'

    shoes_sku_id = fields.Many2one(
        'shoes.sku', string='SKU', ondelete='set null', index=True
    )
    video_file = fields.Binary('Video', attachment=True)
