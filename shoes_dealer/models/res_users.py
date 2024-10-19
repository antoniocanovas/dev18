# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    top_sales = fields.Boolean('Top sales', default=False, help='Enable top sales column in sales view')
