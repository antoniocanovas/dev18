# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ShoesModelMaterial(models.Model):
    _inherit = 'shoes.model.material'

    # Valores heredados de la carta de color, PARA EL FABRICANTE DEL MODELO:
    @api.depends('task_id')
    def _get_manufacturer_campaign_materials(self):
        for record in self:
            materials = set()
            shoes_color_chart_items = self.env['shoes.color.chart.item'].search([
                ('shoes_campaign_id','=',record.task_id.project_id.id),
                ('manufacturer_id','=',record.task_id.manufacturer_id.id)
            ])
            used_materials = set()
            for li in record.shoes_model_material_ids:
                used_materials.add(li.material_id.id)
            for li in shoes_color_chart_items:
                if li.material_id.id not in used_materials:
                    materials.add(li.material_id.id)
            record['material_value_ids'] = [(6,0,materials)]
    material_value_ids = fields.Many2many('product.material', string='Materials',
                                          compute='_get_manufacturer_campaign_materials')
