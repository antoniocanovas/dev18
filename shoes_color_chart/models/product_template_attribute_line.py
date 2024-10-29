# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'


    def _get_valid_product_attribute_values(self):
        for record in self:
            color_attribute = self.env.company.color_attribute_id
            if record.attribute_id == color_attribute:
                values = record.product_tmpl_id.shoes_campaign_id.color_attribute_ids.ids
            else:
                values = self.env['product.attribute.value'].search([('attribute_id','=',record.attribute_id.id)]).ids
            record['campaign_value_ids'] = [(6,0,values)]
    campaign_value_ids = fields.Many2many('product.attribute.value', compute='_get_valid_product_attribute_values')
