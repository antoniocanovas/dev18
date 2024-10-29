# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    shoes_color_chart_id = fields.Many2one('shoes.color.chart.item', related='shoes_task_id.shoes_color_chart_id')
    material_id = fields.Many2one('product.material', related='shoes_task_id.shoes_color_chart_id.material_id')
    manufacturer_id = fields.Many2one('res.partner', related='shoes_task_id.shoes_color_chart_id.manufacturer_id')