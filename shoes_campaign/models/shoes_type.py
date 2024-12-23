# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models

class ShoesType(models.Model):
    _name = 'shoes.type'
    _description = 'Shoes type'

    name = fields.Char('Name', required=True, translate=True)
