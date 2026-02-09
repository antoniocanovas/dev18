# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'


    @api.depends('attribute_id', 'product_tmpl_id.manufacturer_id', 'product_tmpl_id.material_id', 'product_tmpl_id.shoes_campaign_id')
    def _get_valid_product_attribute_values(self):
        for record in self:
            values = set()
            color_attribute = self.env.company.color_attribute_id
            if record.attribute_id == color_attribute and record.product_tmpl_id:
                chart_items = self.env['shoes.color.chart.item'].search([
                    ('manufacturer_id','=',record.product_tmpl_id.manufacturer_id.id),
                    ('material_id','=',record.product_tmpl_id.material_id.id),
                    ('shoes_campaign_id','=',record.product_tmpl_id.shoes_campaign_id.id)
                ])
                for li in chart_items:
                    values.add(li.color_value_id.id)
            else:
                values = self.env['product.attribute.value'].search([('attribute_id','=',record.attribute_id.id)]).ids
            record.campaign_value_ids = [(6, 0, list(values))]
            
    campaign_value_ids = fields.Many2many('product.attribute.value', compute='_get_valid_product_attribute_values')
