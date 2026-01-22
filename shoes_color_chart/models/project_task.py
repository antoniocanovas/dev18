# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"

    shoes_color_chart_id = fields.Many2one('shoes.color.chart.item')
    material_id = fields.Many2one('product.material', string='Material', ondelete='restrict')
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')

    # Campos heredados de la carta de color del proyecto para filtrar valores disponibles en los modelos:
    color_value_ids = fields.Many2many(related='project_id.color_value_ids')
    manufacturer_value_ids = fields.Many2many(related='project_id.manufacturer_value_ids')

    # Para filtrar en vistas de material auxiliar para composición a efectos de marketing:
    project_auxiliar_material_id = fields.Many2one('project.project', string='Auxiliar material',
                                                   compute='_get_project_auxiliar_material')
    def _get_project_auxiliar_material(self):
        self.project_auxiliar_material_id = self.env.company.project_auxiliar_material_id