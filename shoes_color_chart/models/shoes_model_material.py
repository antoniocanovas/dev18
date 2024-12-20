# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ShoesModelMaterial(models.Model):
    _inherit = 'shoes.model.material'

    # Valores heredados de la carta de color:
    material_value_ids = fields.Many2many(related='task_id.project_id.material_value_ids')