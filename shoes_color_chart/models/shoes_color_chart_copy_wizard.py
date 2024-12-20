# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShoesColorChartCopyWizard(models.TransientModel):
    _name = "shoes.color.chart.copy.wizard"
    _description = "Shoes color chart copy wizard"


    shoes_campaign_id = fields.Many2one('project.project', string="Campaign")
    project_id = fields.Many2one('project.project', string="Origin Chart")
    def action_apply(self):
        for li in self.project_id.shoes_color_chart_item_ids:
            newline = self.env['shoes.color.chart.item'].create({
                'shoes_campaign_id': self.shoes_campaign_id.id,
                'manufacturer_id': li.manufacturer_id.id,
                'material_id': li.material_id.id,
                'color_value_id': li.color_value_id.id,
                'name': self.shoes_campaign_id.name + li.manufacturer_id.ref + li.material_id.code
            })