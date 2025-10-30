# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ShoesLast(models.Model):
    _name = "shoes.last"
    _description = "Shoes MRP last"

    name = fields.Char("Name", translate=True)
    heel_id = fields.Many2one("shoes.heel", string="Heel")
    heel_height = fields.Float("Heel height")
    toe = fields.Selection(
        [
            ("pointed", "Pointed"),
            ("square", "Square"),
            ("round", "Round"),
        ],
        string="Toe",
    )
    platform_height = fields.Float("Platform height")
    sole_material_main_id = fields.Many2one(
        "product.material", string="Sole", ondelete="restrict"
    )
    sole_material_secondary_id = fields.Many2one(
        "product.material", string="Sock", ondelete="restrict"
    )
    sole_material_main_percent = fields.Float("Sole main (%)")
    sole_material_secondary_percent = fields.Float("Sole 2nd (%)")
    insole_material_id = fields.Many2one(
        "product.material", string="Insole", ondelete="restrict"
    )
    insole_material_percent = fields.Float("Insole material (%)")
    platform_material_id = fields.Many2one(
        "product.material", string="Platform", ondelete="restrict"
    )
    platform_material_percent = fields.Float("Platform (%)")
    description = fields.Text("Description", translate=True)
