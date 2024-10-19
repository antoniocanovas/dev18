from odoo import _, api, fields, models
from datetime import datetime, date

class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo para heredar en sale.order:
    referrer_id = fields.Many2one('res.partner', 'Referrer', domain=[('grade_id', '!=', False)])

    # Campos para ampliar funcionalidad de comisionistas:
    manager_id = fields.Many2one('res.partner', 'Manager', domain=[('grade_id', '!=', False)], tracking=True)

    @api.model
    def _default_manager_commission_plan(self):
        return self.manager_id.grade_id.default_commission_plan_id
    manager_commission_plan_id = fields.Many2one('commission.plan', 'Manager Plan',
                                                 default=_default_manager_commission_plan,
                                                 tracking=True)
