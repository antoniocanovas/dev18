# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class EutrAudit(models.Model):
    _name = 'eutr.audit'
    _description = 'EUTR Audit'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char('Name', translate=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    date_from = fields.Date('From')
    date_to   = fields.Date('To')
    notes = fields.Html('Comments',  copy=False , translate=True)
    line_ids = fields.One2many('eutr.audit.line','eutr_audit_id', string='Lines')

    def compute_eutr_audit(self):


        return True

    """ Campos de la línea impresa del informe para ser tenidos en cuenta:
    
    product_id = fields.Many2one('product.product', string='Product')
    intrastat_code_id = fields.Many2one(related='product_id.intrastat_code_id', string='Intrastat')
    eutr_nc_code = fields.Char('NC', related='product_id.eutr_nc_code')
    qty      = fields.Float('Quantity (TM)')
    state_id = fields.Many2one('res.country.state', string='State')
    country_id = fields.Many2one('res.country', string='Country')
    eutr_cdc = fields.Boolean('CDC', help='Custody chain')
    eutr_cl  = fields.Boolean('CL', help='Legal control')

    name = fields.Char('Name' , related='product_id.material_id.alias')
    eutr_audit_id = fields.Many2one('eutr.audit', string='EUTR Audit')

    """