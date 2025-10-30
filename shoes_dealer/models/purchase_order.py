# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Comercialmente en cada pedido quieren saber cuántos pares se han comprado:
    def _get_shoes_pair_count(self):
        for record in self:
            record['pairs_count'] = sum(li.pairs_count for li in record.order_line)

    pairs_count = fields.Integer('Pairs', store=False, compute='_get_shoes_pair_count')

    shoes_campaign_id = fields.Many2one('project.project', string="Campaign", store=True, copy=True, tracking=10)
