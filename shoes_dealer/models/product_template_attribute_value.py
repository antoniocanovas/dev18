# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ProductTemplateAttributeValue(models.Model):
    _inherit = 'product.template.attribute.value'


    def _unlink_unused_attributes_from_assortment_to_pairs(self):
        for record in self:
            # Trabajo sobre PTAV, que apunta PTAL, que sólo tiene un tipo de atributo y varios valores a chequear:
            color_attribute = self.env.company.color_attribute_id.id
            size_attribute = self.env.company.size_attribute_id.id
            assortment_attribute = self.env.company.bom_attribute_id.id

            pt_single = record.product_tmpl_id.product_tmpl_single_id
            attribute = record.attribute_id
            ptal = record.attribute_line_id
            value = record.product_attribute_value_id

            if (record.product_tmpl_id.is_assortment) and (pt_single.id):
                # Los colores se pueden borrar directamente ya que tienen relacion directa con pt_single:
                # Como mejora, busca en todos los colores, no sólo en el que se borra (como abajo en surtidos)
                if (attribute.id == color_attribute):
                    ptal_color_single = self.env['product.template.attribute.line'].search(
                        [('product_tmpl_id', '=', pt_single.id), ('attribute_id', '=', attribute.id)])
                    for color in ptal_color_single.value_ids:
                        if color.id not in ptal.value_ids.ids:
                            ptal_color_single['value_ids'] = [(3, color.id)]
                            ptal_color_single._update_product_template_attribute_values()

                # Ahora la posible eliminación de un surtido:
                if (attribute.id == assortment_attribute):
                    sizes = []
                    # PTAL de tallas en pares:
                    ptal_size_single = self.env['product.template.attribute.line'].search(
                        [('product_tmpl_id', '=', pt_single.id), ('attribute_id', '=', size_attribute)])
                    # PTAL surtidos del modelo, para buscar después todas las tallas:
                    for val in ptal.value_ids:
                        for size in val.set_template_id.line_ids:
                            if size.id not in sizes: sizes.append(size.id)
                    # Revisión desde PT PAR para eliminar las tallas que sobran:
                    for val in ptal_size_single.value_ids:
                        if val.id not in sizes:
                            ptal_size_single['value_ids'] = [(3, val.id)]
                            ptal_size_single._update_product_template_attribute_values()

