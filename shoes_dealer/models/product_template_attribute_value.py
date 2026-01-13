from odoo import models


class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _unlink_unused_attributes_from_assortment_to_pairs(self):
        for record in self:
            # Get attribute IDs from the company settings
            color_attribute_id = self.env.company.color_attribute_id.id
            size_attribute_id = self.env.company.size_attribute_id.id
            assortment_attribute_id = self.env.company.assortment_attribute_id.id

            pt_single = record.product_tmpl_id.product_tmpl_single_id
            attribute_id = record.attribute_id.id
            ptal = record.attribute_line_id

            if record.product_tmpl_id.is_assortment and pt_single:
                # Handle color attributes
                if attribute_id == color_attribute_id:
                    ptal_color_single = self.env[
                        "product.template.attribute.line"
                    ].search(
                        [
                            ("product_tmpl_id", "=", pt_single.id),
                            ("attribute_id", "=", attribute_id),
                        ]
                    )
                    ptal_value_ids = ptal.value_ids.ids  # bind loop var
                    unused_colors = ptal_color_single.value_ids.filtered(
                        lambda color, ptal_value_ids=ptal_value_ids: color.id
                        not in ptal_value_ids
                    )
                    if unused_colors:
                        ptal_color_single.write(
                            {"value_ids": [(3, color.id) for color in unused_colors]}
                        )
                        ptal_color_single._update_product_template_attribute_values()

                # Handle assortment attributes
                elif attribute_id == assortment_attribute_id:
                    ptal_size_single = self.env[
                        "product.template.attribute.line"
                    ].search(
                        [
                            ("product_tmpl_id", "=", pt_single.id),
                            ("attribute_id", "=", size_attribute_id),
                        ]
                    )
                    sizes = {
                        size.id
                        for val in ptal.value_ids
                        for size in val.assortment_id.line_ids
                    }
                    sizes_set = set(sizes)  # bind loop var
                    unused_sizes = ptal_size_single.value_ids.filtered(
                        lambda val, sizes_set=sizes_set: val.id not in sizes_set
                    )
                    if unused_sizes:
                        ptal_size_single.write(
                            {"value_ids": [(3, val.id) for val in unused_sizes]}
                        )
                        ptal_size_single._update_product_template_attribute_values()
