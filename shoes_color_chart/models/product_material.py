# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import api, fields, models


class ProductMaterial(models.Model):
    _inherit = "product.material"

    display_name = fields.Char(
        string="Display name", compute="_compute_display_name", store=True
    )
    manufacturer_id = fields.Many2one(
        "res.partner", string="Manufacturer", ondelete="restrict"
    )
    manufacturer_code = fields.Char(related="manufacturer_id.ref")
    material_manufacturer_code = fields.Char(
        "MM code",
        help="Material & manufacturer concatenated code",
        store=True,
        compute="_get_material_manufacturer_code",
    )
    shoes_campaign_ids = fields.Many2many(
        "project.project",
        string="Campaigns",
        domain="['|', ('is_shoes_campaign','=',True), ('id','=',company_project_auxiliar_material_id)]",
    )
    company_project_auxiliar_material_id = fields.Many2one(
        "project.project",
        compute="_compute_company_project_auxiliar_material_id",
    )

    def _compute_company_project_auxiliar_material_id(self):
        project = self.env.company.project_auxiliar_material_id
        for rec in self:
            rec.company_project_auxiliar_material_id = project

    @api.depends("name", "code", "manufacturer_code")
    def _compute_display_name(self):
        for record in self:
            if record.name and record.code and record.manufacturer_code:
                record.display_name = (
                    f"({record.manufacturer_code}{record.code}) {record.name}"
                )
            elif record.name and record.code:
                record.display_name = f"({record.code}) {record.name}"
            elif record.name:
                record.display_name = record.name
            elif record.code:
                record.display_name = record.code
            else:
                record.display_name = False

    @api.depends("code", "manufacturer_code")
    def _get_material_manufacturer_code(self):
        for record in self:
            code = ""
            if record.code:
                code += record.code
            if record.manufacturer_code:
                code += record.manufacturer_code
            record["material_manufacturer_code"] = code
