from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    width_length_high = fields.Char(string="W×L×H (cm)")
