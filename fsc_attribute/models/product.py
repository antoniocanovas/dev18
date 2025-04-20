from odoo import _, api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    fsc_material_value_id = fields.Many2one('product.attribute.value', string='Material', compute='_get_fsc_material_value_id')
    fsc_dimension_value_id = fields.Many2one('product.attribute.value', string='Dimension', store=True, compute='_get_fsc_dimension_value_id')
    fsc_quality_value_id = fields.Many2one('product.attribute.value', string='Quality', store=True, compute='_get_fsc_quality_value_id')

    @api.depends('product_template_variant_value_ids')
    def _get_fsc_material_value_id(self):
        attribute = self.env.company.fsc_material_attribute_id
        value = self.env['product.template.attribute.value'].search([
            ('id','in',product_template_variant_value_ids),
            ('attribute_id','=',attribute.id),
        ]).product_attribute_value_id
        self.fsc_material_value_id = value

    @api.depends('product_template_variant_value_ids')
    def _get_fsc_dimension_value_id(self):
        attribute = self.env.company.fsc_dimension_attribute_id
        return True

    @api.depends('product_template_variant_value_ids')
    def _get_fsc_quality_value_id(self):
        attribute = self.env.company.fsc_quality_attribute_id
        return True


    """
    (SI) product_template_variant_value_ids en product.product apunta a product.template.attribute.value
    (NO) product_template_attribute_value_ids en product.product apunta a product.template.attribute.value
    """