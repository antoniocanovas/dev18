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

