# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api

class ProjectProject(models.Model):
    _inherit = "project.project"


    # Carta de colores:
    shoes_color_chart_item_ids = fields.One2many(
        'shoes.color.chart.item', 'shoes_campaign_id', string='Color template')

    # Utilizado para enviar valor al wizard de color_chart:
    color_attribute_id = fields.Many2one(
        "product.attribute",
        string="Color Attribute",
        store=False,
        default=lambda self: self.env.user.company_id.color_attribute_id,
    )

    shoes_color_chart_item_count = fields.Integer(
        'Chart items',
        store=False,
        default=lambda self: len(self.shoes_color_chart_item_ids),
    )

    # Colores no repetidos para poder llevarlos como dominio a disponibles en product.template:
    def _get_campaign_colors(self):
        colors = set()
        for li in self.shoes_color_chart_item_ids:
            colors.add(li.color_value_id.id)
        self.color_value_ids = [(6,0,colors)]
    color_value_ids = fields.Many2many('product.attribute.value', string="Campaign colors", compute='_get_campaign_colors')
