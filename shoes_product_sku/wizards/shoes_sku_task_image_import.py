# Copyright 2024 Ingenieriacloud.com

from odoo import fields, models


class ShoesSkuTaskImageImport(models.TransientModel):
    _name = 'shoes.sku.task.image.import'
    _description = 'SKU Task Image Import Wizard'

    task_id = fields.Many2one('project.task', string='Model', readonly=True)
    line_ids = fields.One2many(
        'shoes.sku.task.image.import.line', 'wizard_id', string='SKU Lines'
    )


class ShoesSkuTaskImageImportLine(models.TransientModel):
    _name = 'shoes.sku.task.image.import.line'
    _description = 'SKU Task Image Import Wizard Line'

    wizard_id = fields.Many2one('shoes.sku.task.image.import', required=True, ondelete='cascade')
    shoes_sku_id = fields.Many2one('shoes.sku', string='SKU', readonly=True)
    image = fields.Image(related='shoes_sku_id.image_128', readonly=True)
    color_value_id = fields.Many2one(
        'product.attribute.value', related='shoes_sku_id.color_value_id', readonly=True
    )
    existing_image_count = fields.Integer(
        'Uploaded', compute='_compute_existing_image_count'
    )

    def _compute_existing_image_count(self):
        for line in self:
            line.existing_image_count = self.env['product.image'].search_count([
                ('shoes_sku_id', '=', line.shoes_sku_id.id)
            ])

    def action_upload_for_sku(self):
        self.ensure_one()
        return self.shoes_sku_id.action_import_images()

    def action_bulk_upload(self, images):
        """Called from OWL drop widget. images: list of {'name': str, 'data': base64 str}"""
        self.ensure_one()
        ProductImage = self.env['product.image']
        for img in images:
            name = img.get('name', 'image')
            if '.' in name:
                name = name.rsplit('.', 1)[0]
            existing = ProductImage.search([
                ('name', '=', name),
                ('shoes_sku_id', '=', self.shoes_sku_id.id),
            ], limit=1)
            if existing:
                existing.image_1920 = img['data']
            else:
                ProductImage.create({
                    'name': name,
                    'image_1920': img['data'],
                    'shoes_sku_id': self.shoes_sku_id.id,
                })
        return ProductImage.search_count([('shoes_sku_id', '=', self.shoes_sku_id.id)])
