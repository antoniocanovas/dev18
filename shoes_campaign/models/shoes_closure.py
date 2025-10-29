# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models

class ShoesClosure(models.Model):
    _name = 'shoes.closure'
    _description = 'Shoes closure'

    name = fields.Char('Name', required=True, translate=True)
