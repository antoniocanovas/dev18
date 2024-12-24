# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError

class ShoesColorChartItem(models.Model):
    _name = 'shoes.product.sku.item'
    _description = 'Shoes product SKU item'

    name = fields.Char('Name')
    sequence = fields.Integer('Sequence')