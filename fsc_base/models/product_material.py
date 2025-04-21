from odoo import _, api, fields, models

class ProductMaterial(models.Model):
    _inherit = 'product.material'

    fsc_tracking = fields.Boolean('FSC Tracking')
    fsc_fixed = fields.Float('FSC Field (%)')
