# Copyright 2024 Punt Sistemes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _


class ShoesProductCreationWizard(models.TransientModel):
    _name = "shoes.product.creation.wizard"
    _description = "Shoes product creation wizard"

    # Crear productos, proponiendo todos los restantes (deseleccionables) y asignado a la línea el nuevo creado):
    name = fields.Char(related='task_id.name')
    task_id = fields.Many2one('project.task')

    shoes_campaign_id = fields.Many2one(related='task_id.project_id')
    manufacturer_id = fields.Many2one(related='task_id.manufacturer_id')

    def _get_shoes_model_material_ids(self):
        #self.shoes_model_material_ids = [(6,0,self.task_id.shoes_model_material_ids.ids)]
        self.shoes_model_material_ids = []
    shoes_model_material_ids = fields.Many2many('Task Model-materials', compute='_get_shoes_model_material_ids')

    material_ids = fields.Many2many('shoes.model.material', name='Model materials')

    def action_apply(self):
        return True
        """
        for li in material_ids:
            newproduct = self.env['product.template'].with_context(default_task_id=False, default_project_id=False).create({
                'name': self.name,
                'type': 'consu',
                'is_storable': True,
                'shoes_campaign_id': self.task_id.project_id.id,
                'shoes_campaign_ids':[(6,0,[self.task_id.project_id.id])],
                'product_brand_id':self.task_id.product_brand_id.id,
                'manufacturer_id':self.manufacturer_id.id,
                'gender': self.task_id.gender,
                'shoes_pair_weight_id': self.task_id.shoes_pair_weight_id.id,
                'material_id': li.id,
                'shoes_task_id': self.task_id.id,
                'service_tracking': 'no',
                'intrastat_duty_id': self.task_id.intrastat_duty_id.id,
            })
            #self.shoes_product_tmpl_id = newproduct.id
        """