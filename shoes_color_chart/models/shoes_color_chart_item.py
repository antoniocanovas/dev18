# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError

class ShoesColorChartItem(models.Model):
    _name = 'shoes.color.chart.item'
    _description = 'Shoes color chart item'

    name = fields.Char('Name')
    shoes_campaign_id = fields.Many2one('project.project', string='Campaign', domain="[('is_shoes_campaign','=',True)]")
    color_value_id = fields.Many2one('product.attribute.value', string="Color")
    manufacturer_id = fields.Many2one('res.partner', string="Manufacturer")
    material_id = fields.Many2one('product.material', string="Material")
