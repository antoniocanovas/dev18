# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ShoesColorChartItem(models.Model):
    _name = 'shoes.color.chart.item'
    _description = 'Shoes color chart item'

    # Elementos de la tabla de relación de project => valores de atributo tipo color:
    name = fields.Char('Name', compute='_get_color_chart_name')
    shoes_campaign_id = fields.Many2one('project.project', string='Campaign', domain="[('is_shoes_campaign','=',True)]")
    color_value_id = fields.Many2one('product.attribute.value', string="Color")

    # Estos dos los usaré para agrupar en la vista de "Items de paleta de colores":
    manufacturer_id = fields.Many2one('res.partner', related='color_value_id.partner_id')
    material_id = fields.Many2one('product.material', related='color_value_id.material_id')

    def _get_color_chart_name(self):
        for record in self:
            self.name = 'Hola'