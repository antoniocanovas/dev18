# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    # Para componer el default_code del producto automáticamente:
    shoes_default_code_prefix = fields.Char('Internal ref. prefix')
    shoes_default_code_sufix = fields.Char(
        'Internal ref. sufix',
        default=lambda self: self.env.company.shoes_sufix_model_code_prefix + self.project_id.name
    )

    shoes_sku_ids = fields.One2many('shoes.sku', 'shoes_task_id', string='SKU')
    shoes_sku_count = fields.Integer('SKU', compute='_compute_shoes_sku_count')

    @api.depends('shoes_sku_ids')
    def _compute_shoes_sku_count(self):
        for task in self:
            task.shoes_sku_count = len(task.shoes_sku_ids)

    def action_view_shoes_sku(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'SKU',
            'res_model': 'shoes.sku',
            'view_mode': 'list,form',
            'domain': [('shoes_task_id', '=', self.id)],
            'context': {'create': False, 'default_shoes_task_id': self.id},
        }

    def shoes_create_product(self):
        for record in self:
            super(ProjectTask, record).shoes_create_product()
            seq = self.env.company.shoes_sku_sequence_id
            for item in record.shoes_color_chart_item_ids:
                existing = self.env['shoes.sku'].search([
                    ('shoes_task_id', '=', record.id),
                    ('color_value_id', '=', item.color_value_id.id),
                ], limit=1)
                if not existing:
                    name = seq.next_by_id() if seq else self.env['ir.sequence'].next_by_code('shoes.sku') or '/'
                    self.env['shoes.sku'].create({
                        'name': name,
                        'shoes_task_id': record.id,
                        'color_value_id': item.color_value_id.id,
                        'image': record.displayed_image_id.datas,
                    })
