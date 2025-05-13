# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class EutrAuditLine(models.Model):
    _name = 'eudr.audit.line'
    _description = 'EUDR audit line'


    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char('Name' , related='product_id.material_id.alias')
    eutr_audit_id = fields.Many2one('eutr.audit', string='EUTR Audit')

    intrastat_code_id = fields.Many2one(related='product_id.intrastat_code_id', string='Intrastat')
    eudr_nc_code = fields.Char('NC', related='product_id.eudr_nc_code')
    qty      = fields.Float('Quantity (TM)')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    eudr_cdc = fields.Boolean('CDC', help='Custody chain')
    eudr_cl  = fields.Boolean('CL', help='Legal control')