# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    color_value_ids = fields.Many2many('product.attribute.value', related='product_tmpl_id.shoes_color_chart_id.color_value_ids')
