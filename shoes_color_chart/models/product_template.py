# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    material_id = fields.Many2one('product.material', related='shoes_task_id.material_id')
    manufacturer_id = fields.Many2one('res.partner', related='shoes_task_id.manufacturer_id')

    def update_color_values_from_campaign_chart_colors(self):
        for record in self:
            if record.shoes_campaign_id.id and record.shoes_campaign_id.shoes_color_chart_item_ids.ids:
                color_attribute = self.env.company_id.color_attribute_id
                colors = set()
                chart_items = self.env['shoes.color.chart.item'].search(
                    [('shoes_campaign_id', '=', record.shoes_campaign_id.id),
                     ('material_id', '=', record.material_id.id)])
                for li in chart_items:
                    colors.add(li.color_value_id.id)

                ptal = self.env['product.template.attribute.line'].search(
                    [('product_tmpl_id', '=', record.id), ('attribute_id', '=', color_attribute.id)])
                if not ptal.id:
                    ptal = self.env['product.template.attribute.line'].create({
                        'product_tmpl_id': record.id, 'attribute_id': color_attribute.id,
                         'value_ids': [(6, 0, colors)]
                    })
                else:
                    ptal['value_ids'] = [(6, 0, colors)]
            else:
                raise UserError('Producto sin campaña o paleta de color.')