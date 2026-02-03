# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"

    shoes_color_chart_id = fields.Many2one('shoes.color.chart.item')
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')

    # Campos heredados de la carta de color del proyecto para filtrar valores disponibles en los modelos:
    manufacturer_value_ids = fields.Many2many(related='project_id.manufacturer_value_ids')

    color_value_ids = fields.Many2many(string='Colors', compute='_get_color_values')
    def _get_color_values(self):
        colors = self.shoes_color_chart_item_ids.color_value_id.ids
        self.color_value_ids = [(6,0,colors)]

    # Para filtrar en vistas de material auxiliar para composición a efectos de marketing:
    project_auxiliar_material_id = fields.Many2one('project.project', string='Auxiliar material',
                                                   compute='_get_project_auxiliar_material')
    def _get_project_auxiliar_material(self):
        self.project_auxiliar_material_id = self.env.company.project_auxiliar_material_id

    # Colores para este modelo, en base a los disponibles en la carta de color:
    shoes_color_chart_item_ids = fields.Many2many('shoes.color.chart.item', string='Colors')

    shoes_chart_item_used_ids = fields.Many2many(
        'shoes.color.chart.item',
        string='Used colors',
        compute='_compute_shoes_chart_item_used_ids'
    )

    @api.depends('shoes_product_tmpl_id.attribute_line_ids.value_ids', 'shoes_material_id', 'manufacturer_id', 'project_id')
    def _compute_shoes_chart_item_used_ids(self):
        for record in self:
            used_chart_items_ids = []
            if record.shoes_product_tmpl_id and record.env.company.color_attribute_id:
                product_template_attribute_line = record.shoes_product_tmpl_id.attribute_line_ids.filtered(
                    lambda line: line.attribute_id == record.env.company.color_attribute_id
                )
                if product_template_attribute_line:
                    color_values = product_template_attribute_line.value_ids
                    chart_items = self.env['shoes.color.chart.item'].search(
                        [('color_value_id', 'in', color_values.ids),
                         ('material_id', '=', record.shoes_material_id.id),
                         ('manufacturer_id', '=', record.manufacturer_id.id),
                         ('shoes_campaign_id', '=', record.project_id.id)]
                    )
                    used_chart_items_ids = chart_items.ids
            record.shoes_chart_item_used_ids = [(6, 0, used_chart_items_ids)]

    # Valores heredados de la carta de color, PARA EL FABRICANTE DEL MODELO:
    material_value_ids = fields.Many2many(
        'product.material', string='Materials',
        compute='_get_manufacturer_campaign_materials'
    )
    @api.depends('manufacturer_id')
    def _get_manufacturer_campaign_materials(self):
        for record in self.filtered('manufacturer_id'):
            materials = self.env['shoes.color.chart.item'].search([
                ('shoes_campaign_id', '=', record.project_id.id),
                ('manufacturer_id', '=', record.manufacturer_id.id)
            ]).mapped('material_id')
            record.material_value_ids = [(6, 0, materials.ids)]

    def shoes_create_product(self):
        if not self.shoes_color_chart_item_ids:
            raise UserError("Required colors before product creation")
        res = super(ProjectTask, self).shoes_create_product()
        color_attribute_id = self.env.company.color_attribute_id
        if color_attribute_id and self.shoes_product_tmpl_id:
            self.shoes_product_tmpl_id.write({
                'attribute_line_ids': [(0, 0, {
                    'attribute_id': color_attribute_id.id,
                    'value_ids': [(6, 0, self.shoes_color_chart_item_ids.mapped('color_value_id').ids)]
                })]
            })
        return res
