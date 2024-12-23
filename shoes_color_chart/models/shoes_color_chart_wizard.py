# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShoesColorChartWizard(models.TransientModel):
    _name = "shoes.color.chart.wizard"
    _description = "Shoes color chart wizard"


    #    name = fields.Char = fields.Char('Name', related='shoes_campaign_id.name')
    shoes_campaign_id = fields.Many2one('project.project', string="Campaign")
    manufacturer_id = fields.Many2one('res.partner', string="Manufacturer", required=True)
    material_id = fields.Many2one('product.material', string="Material", required=True)
    color_value_ids = fields.Many2many('product.attribute.value', string='Colors', required=True)
    color_attribute_id = fields.Many2one("product.attribute", related='shoes_campaign_id.color_attribute_id')

    def action_apply(self):
        # Chequeo de referencias y códigos requeridos para componer el campo name:
        message = ""
        if self.manufacturer_id.ref == "":
            message = "Manufacturer referencer required (Manufacturer => Sale/Purchases => Reference)"
        if self.material_id.code == "":
            message = "Material code required => (Naterial => Code)"
        for li in self.color_value_ids:
            if li.code == "":
                message = "Color code required (Color => Code): " + li.name

        # Creación de ítems en carta de color:
        for li in self.color_value_ids:
            self.env['shoes.color.chart.item'].create({
                'shoes_campaign_id': self.shoes_campaign_id.id,
                'manufacturer_id': self.manufacturer_id.id,
                'material_id': self.material_id.id,
                'color_value_id': li.id,
                'name': self.shoes_campaign_id.name + "-" + self.material_id.code + self.manufacturer_id.ref + "-" + li.name
            })
