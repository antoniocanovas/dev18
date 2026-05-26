# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = 'project.project'

    shoes_sku_ids = fields.One2many('shoes.sku', 'shoes_campaign_id', string='SKU')
    shoes_sku_count = fields.Integer('SKU', compute='_compute_shoes_sku_count')

    @api.depends('shoes_sku_ids')
    def _compute_shoes_sku_count(self):
        for project in self:
            project.shoes_sku_count = len(project.shoes_sku_ids)

    def action_view_shoes_sku(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'SKU',
            'res_model': 'shoes.sku',
            'view_mode': 'list,form',
            'domain': [('shoes_campaign_id', '=', self.id)],
            'context': {'create': False, 'default_shoes_campaign_id': self.id},
        }

    shoes_referrer_ids = fields.One2many('shoes.stock.referrer', 'shoes_campaign_id', string='Referrers Stock')
    shoes_referrer_count = fields.Integer('Referrers', compute='_compute_shoes_referrer_count')

    @api.depends('shoes_referrer_ids')
    def _compute_shoes_referrer_count(self):
        for project in self:
            project.shoes_referrer_count = len(project.shoes_referrer_ids)

    def action_view_referrers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Referrers Stock',
            'res_model': 'shoes.stock.referrer',
            'view_mode': 'list,form',
            'domain': [('shoes_campaign_id', '=', self.id)],
            'context': {'default_shoes_campaign_id': self.id},
        }

    def action_import_sku_images(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import SKU Images / Videos',
            'res_model': 'shoes.sku.image.import',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_shoes_campaign_id': self.id},
        }
