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

    #pending_product_material_ids = fields.Many2many(related='task_id.pending_product_material_ids')
    #material_ids = fields.Many2many('product.material', string="Materials", required=True)

    def _get_shoes_model_material_ids(self):
        self.shoes_model_material_ids = [(6,0,self.task_id._get_shoes_model_material_ids.ids)]
    shoes_model_material_ids = fields.Many2many(string='Model-material', compute='_get_shoes_model_material_ids')

    material_ids = fields.Many2many('shoes.model.material', name='Model materials')

    def action_apply(self):
        return True
