# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    manufacturer_id = fields.Many2one(
        'res.partner', related='shoes_task_id.manufacturer_id'
    )

    def update_color_values_from_campaign_chart_colors(self):
        for record in self:
            if (
                record.shoes_campaign_id.id
                and record.shoes_campaign_id.shoes_color_chart_item_ids.ids
            ):
                color_attribute = self.env.company.color_attribute_id
                colors = set()
                chart_items = self.env['shoes.color.chart.item'].search(
                    [
                        ('shoes_campaign_id', '=', record.shoes_campaign_id.id),
                        # Esto del material hay que revisarlo y cambiarlo
                        # por el atributo tipo color (como abajo):
                        ('material_id', '=', record.material_id.id),
                    ]
                )
                for li in chart_items:
                    colors.add(li.color_value_id.id)

                ptal = self.env['product.template.attribute.line'].search(
                    [
                        ('product_tmpl_id', '=', record.id),
                        ('attribute_id', '=', color_attribute.id),
                    ]
                )
                if not ptal.id:
                    ptal = self.env['product.template.attribute.line'].create(
                        {
                            'product_tmpl_id': record.id,
                            'attribute_id': color_attribute.id,
                            'value_ids': [(6, 0, colors)],
                        }
                    )
                else:
                    ptal['value_ids'] = [(6, 0, colors)]
            else:
                raise UserError('Producto sin campaña o paleta de color.')

    def action_update_variant_color_size_assortment(self):
        """Server action to update color_value_id, size_value_id and
        assortment_attribute_id on variants depending on product type."""
        for record in self:
            for variant in record.product_variant_ids:
                vals = {}
                color = variant._get_color_attribute_value()
                if color:
                    vals['color_value_id'] = color
                if record.is_pair:
                    size = variant._get_size_attribute_value()
                    if size:
                        vals['size_value_id'] = size
                if record.is_assortment:
                    assortment = variant._get_assortment_attribute_value()
                    if assortment:
                        vals['assortment_attribute_id'] = assortment
                if vals:
                    variant.write(vals)

    def update_all_assortment_values_by_gender(self):
        for record in self:
            if record.shoes_campaign_id.id:
                assortment_attribute = self.env.company.assortment_attribute_id
                assortments = self.env['product.attribute.value'].search(
                    [
                        ('gender', 'in', [record.gender, False]),
                        ('attribute_id', '=', assortment_attribute.id),
                    ]
                ).ids

                ptal = self.env['product.template.attribute.line'].search(
                    [
                        ('product_tmpl_id', '=', record.id),
                        ('attribute_id', '=', assortment_attribute.id),
                    ]
                )
                if not ptal.id:
                    ptal = self.env['product.template.attribute.line'].create(
                        {
                            'product_tmpl_id': record.id,
                            'attribute_id': assortment_attribute.id,
                            'value_ids': [(6, 0, assortments)],
                        }
                    )
                else:
                    ptal['value_ids'] = [(6, 0, assortments)]
