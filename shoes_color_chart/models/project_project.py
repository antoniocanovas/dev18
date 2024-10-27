# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = "project.project"


    shoes_color_value_ids = fields.Many2many(
        "product.attribute.value",
        string="Chart colors",
        relation="shoes_color_chart_item",
        column1="shoes_campaign_id",
        column2="color_value_id",
        copy=True,
    )

    shoes_color_chart_item_ids = fields.One2many(
        'shoes.color.chart.item', 'shoes_campaign_id',
        readonly=True, string='Color template')