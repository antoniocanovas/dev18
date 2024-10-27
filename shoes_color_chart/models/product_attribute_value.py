# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    code = fields.Char('Code')

    color_attribute_id = fields.Many2one(
        "product.attribute",
        string="Size Attribute",
        store=False,
        default=lambda self: self.env.user.company_id.color_attribute_id,
    )
