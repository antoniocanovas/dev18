from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    width_length_high = fields.Char(string="W×L×H (cm)")
