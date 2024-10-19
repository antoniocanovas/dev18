# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ShoesHsCode(models.Model):
    _name = 'shoes.hs.code'
    _description = 'Shoes hs code standard'

    name = fields.Char('Name')
    number = fields.Char('Number')
