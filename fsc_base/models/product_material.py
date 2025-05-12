from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ProductMaterial(models.Model):
    _inherit = 'product.material'

    wood_tracking = fields.Boolean('Wood Tracking')
