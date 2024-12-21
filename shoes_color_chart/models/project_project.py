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

    # COLORES no repetidos:
    def _get_campaign_colors(self):
        colors = set()
        for li in self.shoes_color_chart_item_ids:
            colors.add(li.color_value_id.id)
        self.color_value_ids = [(6,0,colors)]
    color_value_ids = fields.Many2many('product.attribute.value', string="Campaign colors", compute='_get_campaign_colors')

    # FABRICANTES no repetidos:
    def _get_campaign_manufacturers(self):
        manufacturers = set()
        for li in self.shoes_color_chart_item_ids:
            manufacturers.add(li.manufacturer_id.id)
        self.manufacturer_value_ids = [(6,0,manufacturers)]
    manufacturer_value_ids = fields.Many2many('res.partner', string="Campaign manufacturers", compute='_get_campaign_manufacturers')

    # MATERIALES no repetidos:
    def _get_campaign_materials(self):
        materials = set()
        for li in self.shoes_color_chart_item_ids:
            materials.add(li.material_id.id)
        self.material_value_ids = [(6,0,materials)]
    material_value_ids = fields.Many2many('product.material', string="Campaign materials", compute='_get_campaign_materials')

