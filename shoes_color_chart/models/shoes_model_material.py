# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ShoesModelMaterial(models.Model):
    _inherit = 'shoes.model.material'

    # Valores heredados de la carta de color, PARA EL FABRICANTE DEL MODELO:
    def _get_manufacturer_campaign_materials(self):
        materials = set()
        for li in self.shoes_color_chart_item_ids:
            if li.manufacturer_id == self.task_id.manufacturer_id:
                materials.add(li.material_id.id)
        self.material_value_ids = [(6,0,materials)]
    material_value_ids = fields.Many2many('product.material', string='Materials', compute='_get_manufacturer_campaign_materials')