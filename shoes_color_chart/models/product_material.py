# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ProductMaterial(models.Model):
    _inherit = 'product.material'

    code = fields.Char('Code')
