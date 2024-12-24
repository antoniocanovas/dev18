# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufacturer_id = fields.Many2one('res.partner', related='shoes_task_id.manufacturer_id')

    def update_color_values_from_campaign_chart_colors(self):
        for record in self:
            if record.shoes_campaign_id.id and record.shoes_campaign_id.shoes_color_chart_item_ids.ids:
                color_attribute = self.env.company.color_attribute_id
                colors = set()
                chart_items = self.env['shoes.color.chart.item'].search(
                    [('shoes_campaign_id', '=', record.shoes_campaign_id.id),
                     # Esto del material hay que revisarlo y cambiarlo por el atributo tipo color (como abajo):
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

    def update_all_assortment_values_by_gender(self):
        for record in self:
            if record.shoes_campaign_id.id:
                assortment_attribute = self.env.company.assortment_attribute_id
                assortments = self.env['product.attribute.value'].search(
                    [('gender', '=', record.gender),
                     ('attribute_id', '=', assortment_attribute.id)]).ids

                ptal = self.env['product.template.attribute.line'].search(
                    [('product_tmpl_id', '=', record.id), ('attribute_id', '=', assortment_attribute.id)])
                if not ptal.id:
                    ptal = self.env['product.template.attribute.line'].create({
                        'product_tmpl_id': record.id, 'attribute_id': assortment_attribute.id,
                        'value_ids': [(6, 0, assortments)]
                    })
                else:
                    ptal['value_ids'] = [(6, 0, assortments)]
