# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ShoesPairWeight(models.Model):
    _name = 'shoes.pair.weight'
    _description = 'Shoes pair standard weight'

    name = fields.Char('Name')
    pair_weight = fields.Float("Pair weight", digits="product.decimal_stock_weight")
    pair_net_weight = fields.Float("Net pair weight", digits="product.decimal_stock_weight")
