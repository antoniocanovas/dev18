from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ProductMaterial(models.Model):
    _inherit = 'product.material'

    fsc_tracking = fields.Boolean('FSC Tracking')
    fsc_mix_estimation = fields.Boolean(
        'Use FSC Mix estimation',
        help='Use an estation percentage of FSC 100% and other certified origen products.'
             'This case requires an separated control of purchases to get this assortment percentages.'
    )
    fsc_mix_percentage = fields.Float('FSC Mix (%)')

    @api.constrains('fsc_mix_percentage')
    def _check_fsc_mix_percentage(self):
        if self.fsc_mix_estimation and self.fsc_mix_percentage <= 0:
            raise UserError('FSC percentage must be greater than 0 !!')