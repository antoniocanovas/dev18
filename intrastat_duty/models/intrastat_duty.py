# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class IntrastatDuty(models.Model):
    _name = 'intrastat.duty'
    _description = 'Intrastat duty'

    name = fields.Char('Name')
    intrastat_id = fields.Many2one('account.intrastat.code', ondelete='restrict', string='Intrastat code')
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    duty = fields.Float('Duty (%)')

    display_name = fields.Char(string='Display name', compute='_compute_display_name', store=True)

    @api.depends('name', 'country_id')
    def _compute_display_name(self):
        for record in self:
            if record.name and record.country_id.id:
                record.display_name = f"({record.country_id.name}) {record.name}"
            elif record.name:
                record.display_name = record.name
            else:
                record.display_name = False