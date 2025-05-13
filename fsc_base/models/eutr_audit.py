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