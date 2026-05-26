# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    shoes_sku_id = fields.Many2one(
        'shoes.sku', string='SKU', ondelete='restrict', index=True, copy=False
    )
    shoes_sku_image_ids = fields.Many2many(
        'product.image',
        compute='_compute_shoes_sku_image_ids',
        string='SKU Media',
    )

    @api.depends('shoes_sku_id.product_image_ids')
    def _compute_shoes_sku_image_ids(self):
        for product in self:
            product.shoes_sku_image_ids = product.shoes_sku_id.product_image_ids

    @api.depends('product_tmpl_id.write_date', 'shoes_sku_id.write_date')
    def _compute_write_date(self):
        super()._compute_write_date()
        now = self.env.cr.now()
        for record in self:
            if record.shoes_sku_id.write_date:
                record.write_date = max(record.write_date or now, record.shoes_sku_id.write_date)

    # Image priority: SKU image > variant image > template image
    def _compute_image_1920(self):
        for record in self:
            record.image_1920 = (
                record.shoes_sku_id.image
                or record.image_variant_1920
                or record.product_tmpl_id.image_1920
            )

    def _compute_image_1024(self):
        for record in self:
            record.image_1024 = (
                record.shoes_sku_id.image_1024
                or record.image_variant_1024
                or record.product_tmpl_id.image_1024
            )

    def _compute_image_512(self):
        for record in self:
            record.image_512 = (
                record.shoes_sku_id.image_512
                or record.image_variant_512
                or record.product_tmpl_id.image_512
            )

    def _compute_image_256(self):
        for record in self:
            record.image_256 = (
                record.shoes_sku_id.image_256
                or record.image_variant_256
                or record.product_tmpl_id.image_256
            )

    def _compute_image_128(self):
        for record in self:
            record.image_128 = (
                record.shoes_sku_id.image_128
                or record.image_variant_128
                or record.product_tmpl_id.image_128
            )

    def create(self, vals_list):
        res = super().create(vals_list)
        pairs_assortments = res.filtered(lambda p: p.is_pair or p.is_assortment)
        if pairs_assortments:
            if self.env.company.shoes_sku_update:
                # _update_product_product_sku already calls _assign_shoes_sku internally
                pairs_assortments.product_tmpl_id._update_product_product_sku()
            else:
                pairs_assortments._assign_shoes_sku()
        return res

    def _assign_shoes_sku(self):
        for product in self:
            if product.shoes_sku_id:
                continue
            task = product.shoes_task_id
            color = product.color_value_id
            if not task:
                continue
            sku = self.env['shoes.sku'].search([
                ('shoes_task_id', '=', task.id),
                ('color_value_id', '=', color.id if color else False),
            ], limit=1)
            if not sku:
                # Try to use a placeholder SKU (no color, no products)
                if color:
                    candidates = self.env['shoes.sku'].search([
                        ('shoes_task_id', '=', task.id),
                        ('color_value_id', '=', False),
                    ])
                    placeholder = candidates.filtered(lambda s: not s.product_ids)[:1]
                    if placeholder:
                        placeholder.write({'color_value_id': color.id})
                        sku = placeholder
                if not sku:
                    seq = self.env.company.shoes_sku_sequence_id
                    name = seq.next_by_id() if seq else self.env['ir.sequence'].next_by_code('shoes.sku') or '/'
                    sku = self.env['shoes.sku'].create({
                        'name': name,
                        'shoes_task_id': task.id,
                        'color_value_id': color.id if color else False,
                        'image': product.product_tmpl_id.image_1920,
                    })
            product.shoes_sku_id = sku.id
