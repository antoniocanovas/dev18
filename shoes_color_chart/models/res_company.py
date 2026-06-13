# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    project_auxiliar_material_id = fields.Many2one(
        'project.project', string='Auxiliar material', store=True,
        help='Project (simulated campaign) to set in general materials not used in campaigns.'
    )
