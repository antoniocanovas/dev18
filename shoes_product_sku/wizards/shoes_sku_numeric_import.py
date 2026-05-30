# Copyright 2024 Ingenieriacloud.com

from odoo import api, fields, models


class ShoesSkuNumericImport(models.TransientModel):
    _name = 'shoes.sku.numeric.import'
    _description = 'SKU Numeric Photo Import Wizard'

    task_id = fields.Many2one('project.task', string='Model', readonly=True)
    line_ids = fields.One2many('shoes.sku.numeric.import.line', 'wizard_id', string='SKU Lines')


class ShoesSkuNumericImportLine(models.TransientModel):
    _name = 'shoes.sku.numeric.import.line'
    _description = 'SKU Numeric Photo Import Line'

    wizard_id = fields.Many2one('shoes.sku.numeric.import', required=True, ondelete='cascade')
    shoes_sku_id = fields.Many2one('shoes.sku', string='SKU', readonly=True)
    color_value_id = fields.Many2one(
        'product.attribute.value', related='shoes_sku_id.color_value_id', readonly=True
    )
    photo_count = fields.Integer(compute='_compute_photo_count')

    @api.depends('shoes_sku_id')
    def _compute_photo_count(self):
        count = self.env.company.shoes_sku_photo_count or 1
        for line in self:
            line.photo_count = count

    # ── RPC methods called from OWL ─────────────────────────────────────────

    def action_upload_slot(self, slot_index, image_data):
        """Upload a single image to slot_index (1 = shoes.sku.image, N = x_imageN)."""
        self.ensure_one()
        sku = self.shoes_sku_id
        if slot_index == 1:
            sku.write({'image': image_data})
        else:
            field_name = f'x_image{slot_index}'
            auto_name = f'{sku.name}_{slot_index}'
            existing = sku[field_name] if field_name in sku._fields else False
            if existing:
                existing.write({'image_1920': image_data})
            else:
                new_img = self.env['product.image'].create({
                    'name': auto_name,
                    'image_1920': image_data,
                    'shoes_sku_id': sku.id,
                })
                sku.write({field_name: new_img.id})
        return self._slot_info(slot_index)

    def get_all_lines_slot_data(self):
        """Batch RPC: returns {str(line_id): [slot_info, ...]} for all lines."""
        result = {}
        count = self.env.company.shoes_sku_photo_count or 1
        for line in self:
            result[str(line.id)] = [line._slot_info(i) for i in range(1, count + 1)]
        return result

    # ── helpers ─────────────────────────────────────────────────────────────

    def _slot_info(self, slot_index):
        sku = self.shoes_sku_id
        if slot_index == 1:
            has = bool(sku.image)
            return {
                'has_image': has,
                'url': f'/web/image/shoes.sku/{sku.id}/image_128' if has else False,
            }
        field_name = f'x_image{slot_index}'
        img = sku[field_name] if field_name in sku._fields else False
        if img:
            return {
                'has_image': True,
                'url': f'/web/image/product.image/{img.id}/image_128',
            }
        return {'has_image': False, 'url': False}
