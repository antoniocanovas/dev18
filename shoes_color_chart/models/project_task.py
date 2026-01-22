# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"

    shoes_color_chart_id = fields.Many2one('shoes.color.chart.item')
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')

    # Campos heredados de la carta de color del proyecto para filtrar valores disponibles en los modelos:
    color_value_ids = fields.Many2many(related='project_id.color_value_ids')
    manufacturer_value_ids = fields.Many2many(related='project_id.manufacturer_value_ids')

    # Para filtrar en vistas de material auxiliar para composición a efectos de marketing:
    project_auxiliar_material_id = fields.Many2one('project.project', string='Auxiliar material',
                                                   compute='_get_project_auxiliar_material')
    def _get_project_auxiliar_material(self):
        self.project_auxiliar_material_id = self.env.company.project_auxiliar_material_id

    # Valores heredados de la carta de color, PARA EL FABRICANTE DEL MODELO:
    material_value_ids = fields.Many2many(
        'product.material', string='Materials',
        compute='_get_manufacturer_campaign_materials'
    )
    @api.depends('manufacturer_id')
    def _get_manufacturer_campaign_materials(self):
        for record in self:
            materials = []
            shoes_color_chart_items = self.env['shoes.color.chart.item'].search([
                ('shoes_campaign_id','=',record.project_id.id),
                ('manufacturer_id','=',record.manufacturer_id.id)
            ])
            if shoes_color_chart_items.material_id.ids:
                materials = shoes_color_chart_items.material_id.ids
            record['material_value_ids'] = [(6,0,materials)]
