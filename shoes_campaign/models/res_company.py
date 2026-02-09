# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'


    shoes_sufix_model_code_prefix = fields.Char(
        string='Sufix mode prefix',
        size=2,
        help='Prefix used in product model sufix code (task model)'
    )
