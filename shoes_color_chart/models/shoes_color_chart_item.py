# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ShoesColorChartItem(models.Model):
    _name = 'shoes.color.chart.item'
    _description = 'Shoes color chart item'

    # Elementos de la tabla de relación de project => valores de atributo tipo color:
    name = fields.Char('Name')
    shoes_campaign_id = fields.Many2one('Campaign')
    color_value_id = fields.Many2one('product.attribute.value')

    # Estos dos los usaré para agrupar en la vista de "Items de paleta de colores":
    manufacturer_id = fields.Many2one('res.partner', related='color_value_id.partner_id')
    material_id = fields.Many2one('product.material', related='color_value_id.material_id')
