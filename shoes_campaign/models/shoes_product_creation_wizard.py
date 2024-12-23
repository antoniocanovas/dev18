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

    shoes_model_material_ids = fields.One2many(related='task_id.shoes_model_material_ids')
    material_ids = fields.Many2many('shoes.model.material', name='Model materials')

    def action_apply(self):
        for record in self:
            for li in record.material_ids:
                newproduct = self.env['product.template'].with_context(default_task_id=False, default_project_id=False).create({
                    'name': "$$." + record.task_id.name,
                    'type': 'consu',
                    'is_storable': True,
                    'shoes_campaign_id': record.task_id.project_id.id,
                    'shoes_campaign_ids':[(6,0,[record.task_id.project_id.id])],
                    'product_brand_id':record.task_id.product_brand_id.id,
                    'manufacturer_id':record.manufacturer_id.id,
                    'gender': record.task_id.gender,
                    'shoes_pair_weight_id': record.task_id.shoes_pair_weight_id.id,
                    'material_id': li.material_id.id,
                    'shoes_last_id': li.shoes_last_id.id,
                    'shoes_task_id': record.task_id.id,
                    'service_tracking': 'no',
                    'intrastat_duty_id': record.task_id.intrastat_duty_id.id,
                })
                li['shoes_product_tmpl_id'] = newproduct.id
