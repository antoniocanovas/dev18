# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShoesColorChartWizard(models.TransientModel):
    _name = "shoes.color.chart.wizard"
    _description = "Shoes color chart wizard"


#    name = fields.Char = fields.Char('Name', related='shoes_campaign_id.name')
    shoes_campaign_id = fields.Many2one('project.project', string="Campaign")
    manufacturer_id = fields.Many2one('res.partner', string="Manufacturer")
    material_id = fields.Many2one('product.material', string="Material")
    color_value_ids = fields.Many2many('product.attribute.value', string='Colors')

    color_attribute_id = fields.Many2one(
        "product.attribute",
        string="Color Attribute",
        store=False,
        default=lambda self: self.env.user.company_id.color_attribute_id,
    )

    def action_apply(self):
        return True