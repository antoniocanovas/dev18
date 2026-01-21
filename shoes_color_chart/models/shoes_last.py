# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models


class ShoesLast(models.Model):
    _inherit = "shoes.last"

    # Para filtrar en vistas de material auxiliar para composición a efectos de marketing:
    project_auxiliar_material_id = fields.Many2one(
        "project.project",
        string="Auxiliar material",
        compute="_get_project_auxiliar_material",
    )

    @api.depends("name")
    def _get_project_auxiliar_material(self):
        self.project_auxiliar_material_id = (
            self.env.company.project_auxiliar_material_id
        )
