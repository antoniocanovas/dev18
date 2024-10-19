# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    material_id = fields.Many2one('product.material', related='product_tmpl_id.material_id')

    @api.constrains('value_ids')
    def _avoid_custom_assortment_values_if_no_tracking(self):
        for record in self:
            if record.product_tmpl_id.tracking != 'serial':
                if record.attribute_id == self.env.company.bom_attribute_id:
                    for value in record.value_ids:
                        if value.is_custom:
                            raise UserError('Product serial tracking required to assign custom assortment values.'
                                            'Got to Inventory tab => Traceability => Serial number, and save again.')
