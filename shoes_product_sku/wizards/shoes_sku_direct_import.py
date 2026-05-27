# Copyright 2024 Ingenieriacloud.com

from odoo import fields, models

VIDEO_MIMETYPES = {
    'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo',
    'video/x-matroska', 'video/webm', 'video/x-m4v', 'video/x-ms-wmv',
    'video/3gpp', 'video/ogg',
}


class ShoesSkuDirectImport(models.TransientModel):
    _name = 'shoes.sku.direct.import'
    _description = 'SKU Direct Image/Video Import Wizard'

    shoes_sku_id = fields.Many2one('shoes.sku', string='SKU', readonly=True)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'shoes_sku_direct_import_att_rel',
        'wizard_id', 'attachment_id',
        string='Files',
    )

    def action_import(self):
        self.ensure_one()

        ProductImage = self.env['product.image']
        created = updated = 0

        for att in self.attachment_ids:
            filename = att.name
            name = filename.rsplit('.', 1)[0] if '.' in filename else filename
            is_video = (att.mimetype or '') in VIDEO_MIMETYPES

            existing = ProductImage.search([
                ('name', '=', name),
                ('shoes_sku_id', '=', self.shoes_sku_id.id),
            ], limit=1)

            vals = (
                {'video_file': att.datas}
                if is_video
                else {'image_1920': att.datas}
            )

            if existing:
                existing.write(vals)
                updated += 1
            else:
                vals.update({'name': name, 'shoes_sku_id': self.shoes_sku_id.id})
                ProductImage.create(vals)
                created += 1

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Import completado',
                'message': f'Creados: {created} | Actualizados: {updated}',
                'type': 'success',
                'sticky': False,
            },
        }
