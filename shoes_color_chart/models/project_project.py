# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = "project.project"


    shoes_color_value_ids = fields.Many2many(
        "product.attribute.value",
        string="Chart colors",
        relation="shoes_color_chart_item",
        column1="shoes_campaign_id",
        column2="color_value_id",
        copy=True,
    )

    # Registros m2m para búsqueda y filtrado posterior, no se usa en las vistas:
    shoes_color_chart_item_ids = fields.One2many(
        'shoes.color.chart.item', 'shoes_campaign_id',
        readonly=True, string='Color template')

    color_attribute_id = fields.Many2one(
        "product.attribute",
        string="Color Attribute",
        store=False,
        default=lambda self: self.env.user.company_id.color_attribute_id,
    )


    @api.constrains('shoes_color_value_ids')
    def _check_manufacturer_partner_and_material_codes_in_color_chart(self):
        for record in self:
            for li in record.shoes_color_value_ids:
                if not li.partner_id.ref or not li.material_id.code:
                    message = "Material, manufacturer and color CODES are required in all lines !!, please check " + li.name
                    raise UserError(message)
