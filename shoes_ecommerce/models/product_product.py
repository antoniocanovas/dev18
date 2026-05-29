# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_images(self):
        self.ensure_one()
        sku = self.shoes_sku_id
        standard = super()._get_images()
        if not sku:
            return standard
        # standard = [self, ...variant_extra_images..., ...template_extra_images...]
        if sku.image:
            # Use SKU record as main carousel image (stored field → reliable image URL)
            images = [sku] + standard[1:]
        else:
            images = list(standard)
        if sku.product_image_ids:
            images = images + list(sku.product_image_ids)
        return images
