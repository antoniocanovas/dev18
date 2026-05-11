from odoo import fields, models


class ProductBrand(models.Model):
    _inherit = "product.brand"

    code = fields.Char(string="Code")
