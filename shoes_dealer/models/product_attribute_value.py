# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    assortment_id = fields.Many2one('shoes.assortment', string='Template', store=True, copy=False)

    # Calcula si el atributo de conjunto debe estar oculto basado en la configuración de la compañía
    def _get_set_hidden(self):
        company_bom_attribute = self.env.user.company_id.assortment_attribute_id
        set_hidden = True
        if (company_bom_attribute.id) and (company_bom_attribute.id == self.attribute_id.id): set_hidden = False
        self.set_hidden = set_hidden
    set_hidden = fields.Boolean('Set hidden', store=False, compute='_get_set_hidden')

    material_id = fields.Many2one('product.material', string='Material')

    # Restringe la creación de valores personalizados para atributos de color y tamaño
    @api.constrains('is_custom')
    def _constrains_no_custom_in_sizes_colors(self):
        for record in self:
            color_attribute = self.env.company.color_attribute_id
            size_attribute = self.env.company.size_attribute_id
            if record.is_custom and record.attribute_id.id in [color_attribute.id, size_attribute.id]:
                raise UserError('Custom color and size values are not allowed, please review.')
