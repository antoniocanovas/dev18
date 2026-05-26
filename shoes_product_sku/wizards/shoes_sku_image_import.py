# Copyright 2024 Ingenieriacloud.com

from odoo import fields, models
from odoo.exceptions import UserError

VIDEO_MIMETYPES = {
    'video/mp4', 'video/avi', 'video/quicktime', 'video/x-msvideo',
    'video/x-matroska', 'video/webm', 'video/x-m4v', 'video/x-ms-wmv',
    'video/3gpp', 'video/ogg',
}


class ShoesSkuImageImport(models.TransientModel):
    _name = 'shoes.sku.image.import'
    _description = 'SKU Image/Video Import Wizard'

    shoes_campaign_id = fields.Many2one('project.project', string='Campaign', readonly=True)
    attachment_ids = fields.Many2many(
        'ir.attachment',
        'shoes_sku_image_import_att_rel',
        'wizard_id', 'attachment_id',
        string='Files',
    )

    def action_import(self):
        self.ensure_one()

        sequence = self.env['ir.sequence'].search([('code', '=', 'shoes.sku')], limit=1)
        padding = sequence.padding if sequence else 5

        errors = []
        valid_items = []

        for att in self.attachment_ids:
            filename = att.name
            name_no_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename

            if len(name_no_ext) < padding:
                errors.append(f"• {filename}: nombre demasiado corto para identificar el SKU ({padding} caracteres)")
                continue

            sku_code = name_no_ext[:padding]
            rest = name_no_ext[padding:]

            # Strip separator only if it appears immediately after the SKU literal
            if rest and rest[0] in ('_', '-'):
                rest = rest[1:]

            image_name = rest or sku_code

            sku = self.env['shoes.sku'].search([('name', '=', sku_code)], limit=1)
            if not sku:
                errors.append(f"• {filename}: SKU '{sku_code}' no encontrado")
                continue

            is_video = (att.mimetype or '') in VIDEO_MIMETYPES

            valid_items.append({
                'sku': sku,
                'name': image_name,
                'content': att.datas,
                'is_video': is_video,
            })

        if errors:
            raise UserError("Errores en los ficheros:\n" + "\n".join(errors))

        ProductImage = self.env['product.image']
        created = updated = 0

        for item in valid_items:
            existing = ProductImage.search([
                ('name', '=', item['name']),
                ('shoes_sku_id', '=', item['sku'].id),
            ], limit=1)

            vals = (
                {'video_file': item['content']}
                if item['is_video']
                else {'image_1920': item['content']}
            )

            if existing:
                existing.write(vals)
                updated += 1
            else:
                vals.update({'name': item['name'], 'shoes_sku_id': item['sku'].id})
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
