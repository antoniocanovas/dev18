# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from fnmatch import translate

from odoo import fields, models, api

class ShoesHeel(models.Model):
    _name = 'shoes.heel'
    _description = 'Shoes Heel'

    name = fields.Char('Name', translate=True)
    active = fields.Boolean('Active', default=True)