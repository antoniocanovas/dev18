from odoo import _, api, fields, models


class ShoesSkuPhotoReduceWizard(models.TransientModel):
    _name = 'shoes.sku.photo.reduce.wizard'
    _description = 'Confirm SKU Photo Count Reduction'

    company_id = fields.Many2one('res.company', required=True)
    new_count = fields.Integer()
    current_count = fields.Integer()
    message = fields.Char(compute='_compute_message')

    @api.depends('new_count', 'current_count')
    def _compute_message(self):
        for rec in self:
            if rec.current_count > rec.new_count + 1:
                field_range = f'x_image{rec.new_count + 1} ... x_image{rec.current_count}'
            else:
                field_range = f'x_image{rec.current_count}'
            rec.message = _(
                'Reducing from %(old)d to %(new)d photos will permanently delete '
                'field(s) %(fields)s on shoes.sku and all linked image data. '
                'This cannot be undone.',
                old=rec.current_count, new=rec.new_count, fields=field_range,
            )

    def action_confirm(self):
        self.ensure_one()
        sku_model = self.env['ir.model'].search([('model', '=', 'shoes.sku')], limit=1)
        self.company_id._update_sku_photo_view(self.new_count)
        self.company_id._delete_sku_photo_fields(self.new_count, self.current_count, sku_model)
        self.company_id.with_context(_sku_photo_reduce_confirmed=True).write(
            {'shoes_sku_photo_count': self.new_count}
        )
        return {'type': 'ir.actions.act_window_close'}
