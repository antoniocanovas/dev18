# Copyright 2020 Hunki Enterprises BV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShoesColorChartCopyWizard(models.TransientModel):
    _name = "shoes.color.chart.copy.wizard"
    _description = "Shoes color chart copy wizard"


    shoes_campaign_id = fields.Many2one('project.project', string="Campaign")
    project_id = fields.Many2one('project.project', string="Origin Chart")
    def action_apply(self):
        return True