# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"

    shoes_color_chart_id = fields.Many2one('shoes.color.chart.item')
    material_id = fields.Many2one('product.material', string='Material')
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')

    # Campos heredados de la carta de color del proyecto para filtrar valores disponibles en los modelos:
    color_value_ids = fields.Many2many(related='project_id.color_value_ids')
    manufacturer_value_ids = fields.Many2many(related='project_id.manufacturer_value_ids')
