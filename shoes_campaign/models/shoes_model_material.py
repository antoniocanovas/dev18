# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models


class ShoesModelMaterial(models.Model):
    _name = "shoes.model.material"
    _description = "Shoes model material"

    name = fields.Char("Name", store=True, compute="_get_name")
    manufacturer_ref = fields.Char("Manufacturer Ref")
    material_id = fields.Many2one(
        "product.material", string="Material", ondelete="restrict"
    )
    shoes_last_id = fields.Many2one("shoes.last", string="Last", ondelete="restrict")
    shoes_product_tmpl_id = fields.Many2one("product.template", string="Product")
    task_id = fields.Many2one("project.task", string="Task", ondelete="restrict")
    shoes_campaign_id = fields.Many2one(related="task_id.project_id")
    # Para añadir QR en tarifas:
    shoes_url = fields.Char("URL")

    @api.depends("material_id", "manufacturer_ref", "task_id.shoes_default_code_prefix")
    def _get_name(self):
        for record in self:
            name = ""
            if record.task_id.shoes_default_code_prefix:
                name += record.task_id.shoes_default_code_prefix
            if record.material_id.code:
                name += record.material_id.code
            if record.task_id.manufacturer_id.ref:
                name += record.task_id.manufacturer_id.ref
            record["name"] = name
