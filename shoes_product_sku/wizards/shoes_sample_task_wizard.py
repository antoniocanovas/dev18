# Copyright 2024 Ingenieriacloud.com

from odoo import fields, models


class ShoesSampleTaskWizard(models.TransientModel):
    _name = 'shoes.sample.task.wizard'
    _description = 'Shoes Sample Task Wizard'

    task_id = fields.Many2one('project.task', readonly=True)
    cell_ids = fields.One2many('shoes.sample.task.wizard.cell', 'wizard_id')

    def action_save(self):
        for cell in self.cell_ids:
            if cell.shoes_sample_id:
                if cell.type:
                    cell.shoes_sample_id.type = cell.type
                else:
                    cell.shoes_sample_id.unlink()
            elif cell.type:
                campaign_id = (
                    cell.shoes_sku_id.shoes_campaign_id.id
                    or self.task_id.project_id.id
                )
                self.env['shoes.sample'].create({
                    'partner_id': cell.partner_id.id,
                    'shoes_campaign_id': campaign_id,
                    'shoes_sku_id': cell.shoes_sku_id.id,
                    'type': cell.type,
                })
        return {'type': 'ir.actions.act_window_close'}


class ShoesSampleTaskWizardCell(models.TransientModel):
    _name = 'shoes.sample.task.wizard.cell'
    _description = 'Shoes Sample Task Wizard Cell'

    wizard_id = fields.Many2one('shoes.sample.task.wizard', required=True)
    shoes_sku_id = fields.Many2one('shoes.sku', required=True)
    color_value_id = fields.Many2one(related='shoes_sku_id.color_value_id')
    partner_id = fields.Many2one('res.partner', required=True)
    type = fields.Char('Type', size=2)
    shoes_sample_id = fields.Many2one('shoes.sample')
