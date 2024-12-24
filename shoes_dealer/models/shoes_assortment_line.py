# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ShoesAssortmentLine(models.Model):
    _name = 'shoes.assortment.line'
    _description = 'Shoes Assortment Line'

    def _get_name(self):
        for record in self:
            record['name'] = str(record.value_id.name) + ": " + str(record.quantity)
    name = fields.Char('Name', store=False, compute='_get_name')

    assortment_id   = fields.Many2one('shoes.assortment', string='assortment', required=True, store=True, copy=True)
    value_id = fields.Many2one('product.attribute.value', string='Value', store=True, required=True, copy=True)
    quantity = fields.Integer('Quantity', store=True, copy=True)
    attribute_id = fields.Many2one('product.attribute', related='assortment_id.attribute_id')