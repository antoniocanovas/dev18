# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"

    shoes_color_chart_id = fields.Many2one('shoes.color.chart.item')
    material_id = fields.Many2one('product.material', related='shoes_color_chart_id.material_id')
    manufacturer_id = fields.Many2one('product.material', related='shoes_color_chart_id.manufacturer_id')