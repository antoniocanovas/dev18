# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import _, api, fields, models
from odoo.exceptions import RedirectWarning, UserError


class ResCompany(models.Model):
    _inherit = 'res.company'

    shoes_sku_item_ids = fields.Many2many('shoes.product.sku.item', string='SKU Items', default=[(6,0,[1,2,3,4,5])])
    shoes_sku_photo_count = fields.Integer(
        string='Photos per SKU',
        default=1,
        help='1 = main image only. For N > 1, fields x_image2...x_imageN are created on shoes.sku.',
    )
    shoes_sku_update = fields.Boolean('Update on creation', default=True, help='Internal ref will be updated on pairs creation.')
    shoes_sku_sequence_id = fields.Many2one(
        'ir.sequence',
        string='SKU Sequence',
        default=lambda self: self.env.ref('shoes_product_sku.shoes_sku_sequence', raise_if_not_found=False),
    )

    # Parametrización para la cadena utilizada en la composición de la referencia interna del producto:
    shoes_code_product = fields.Selection([
        ('code','Code'),('name','Name'),('none','None')],
        string='Product code',
        default='code',
    )
    shoes_code_manufacturer = fields.Selection([
        ('code', 'Code'), ('name', 'Name'), ('none', 'None')],
        string='Manufacturer code',
        default='code',
    )
    shoes_code_color = fields.Selection([
        ('code','Code'),('name','Name'),('none','None')],
        string='Color code',
        default='code',
    )
    shoes_code_material = fields.Selection([
        ('code','Code'),('name','Name'),('none','None')],
        string='Material code',
        default='code',
    )
    shoes_code_campaign = fields.Selection([
        ('code','Code'),('name','Name'),('none','None')],
        string='Campaign code',
        default='name',
    )
    shoes_code_product_prefix = fields.Char(
        string='Product prefix',
        size=2,
    )
    shoes_code_manufacturer_prefix = fields.Char(
        string='Manufacturer prefix',
        size=2,
    )
    shoes_code_color_prefix = fields.Char(
        string='Color prefix',
        size=2,
    )
    shoes_code_material_prefix = fields.Char(
        string='Material prefix',
        size=2,
    )
    shoes_code_campaign_prefix = fields.Char(
        string='Campaign prefix',
        size=2,
    )

    def write(self, vals):
        new_count = vals.get('shoes_sku_photo_count')
        if new_count is not None and not self.env.context.get('_sku_photo_reduce_confirmed'):
            new_count = max(1, int(new_count))
            vals['shoes_sku_photo_count'] = new_count
            sku_model = self.env['ir.model'].search([('model', '=', 'shoes.sku')], limit=1)
            current_count = self._get_current_sku_photo_count(sku_model)
            if new_count < current_count:
                raise RedirectWarning(
                    _(
                        'Reducing the SKU photo count from %(old)d to %(new)d will permanently '
                        'delete fields x_image%(start)d...x_image%(end)d and all linked data.',
                        old=current_count, new=new_count,
                        start=new_count + 1, end=current_count,
                    ),
                    {
                        'type': 'ir.actions.act_window',
                        'name': _('Confirm Photo Field Deletion'),
                        'res_model': 'shoes.sku.photo.reduce.wizard',
                        'views': [(False, 'form')],
                        'target': 'new',
                        'context': {
                            'default_company_id': self[0].id,
                            'default_new_count': new_count,
                            'default_current_count': current_count,
                        },
                    },
                    _('Review and Confirm'),
                )
        result = super().write(vals)
        if new_count is not None and not self.env.context.get('_sku_photo_reduce_confirmed'):
            sku_model = self.env['ir.model'].search([('model', '=', 'shoes.sku')], limit=1)
            current_count = self._get_current_sku_photo_count(sku_model)
            if new_count > current_count:
                self._create_sku_photo_fields(current_count, new_count, sku_model)
            self._update_sku_photo_view(new_count)
        return result

    @api.model
    def _get_current_sku_photo_count(self, sku_model):
        max_n = 1
        for f in self.env['ir.model.fields'].search([('model_id', '=', sku_model.id)]):
            if f.name.startswith('x_image') and f.name[7:].isdigit():
                max_n = max(max_n, int(f.name[7:]))
        return max_n

    def _create_sku_photo_fields(self, current_count, new_count, sku_model):
        Fields = self.env['ir.model.fields']
        for i in range(max(2, current_count + 1), new_count + 1):
            fname = f'x_image{i}'
            if not Fields.search([('name', '=', fname), ('model_id', '=', sku_model.id)], limit=1):
                Fields.create({
                    'name': fname,
                    'model_id': sku_model.id,
                    'field_description': f'Image {i}',
                    'ttype': 'many2one',
                    'relation': 'product.image',
                    'store': True,
                    'copied': False,
                    'on_delete': 'set null',
                })

    def _delete_sku_photo_fields(self, new_count, current_count, sku_model):
        Fields = self.env['ir.model.fields']
        for i in range(new_count + 1, current_count + 1):
            field = Fields.search([
                ('name', '=', f'x_image{i}'), ('model_id', '=', sku_model.id)
            ], limit=1)
            if field:
                field.unlink()

    def _update_sku_photo_view(self, count):
        parent_view = self.env.ref('shoes_product_sku.shoes_sku_form_view', raise_if_not_found=False)
        if not parent_view:
            return
        dyn_view = self.env['ir.ui.view'].search([
            ('name', '=', 'shoes.sku.form.extra.images.dynamic'),
            ('model', '=', 'shoes.sku'),
        ], limit=1)
        if count <= 1:
            if dyn_view:
                dyn_view.unlink()
            return
        fields_xml = ''.join(
            f'<field name="x_image{i}" string="Image {i}"/>' for i in range(2, count + 1)
        )
        arch = (
            '<data>'
            '<xpath expr="//page[@name=\'images\']/field[@name=\'product_image_ids\']" position="before">'
            f'<group string="SKU Images" name="sku_extra_images">{fields_xml}</group>'
            '</xpath>'
            '</data>'
        )
        if dyn_view:
            dyn_view.write({'arch': arch})
        else:
            self.env['ir.ui.view'].create({
                'name': 'shoes.sku.form.extra.images.dynamic',
                'model': 'shoes.sku',
                'inherit_id': parent_view.id,
                'arch': arch,
                'mode': 'extension',
            })

    #  Forzar que todos los parámetros posibles estén establecidos:
    @api.constrains('shoes_sku_item_ids')
    def _ensure_unique_sku(self):
        if len(self.shoes_sku_item_ids.ids) != 5:
            raise UserError('Include all codes to ensure an unique SKU per product.')

