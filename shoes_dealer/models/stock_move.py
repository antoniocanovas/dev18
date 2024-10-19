# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api


class StockMove(models.Model):
    _inherit = "stock.move"

    # Comercialmente en cada Albaran quieren saber cuántos pares se han vendido:
    def _get_shoes_stock_move_pair_count(self):
        for record in self:
            record["pairs_count"] = record.product_id.pairs_count * record.quantity

    @api.depends('move_line_ids.quantity')
    def _get_shoes_stock_move_pair_count(self):
        for move in self:
            move.pairs_count = sum(line.quantity for line in move.move_line_ids) * move.product_id.pairs_count
    pairs_count = fields.Integer(
        "Pairs", store=True, compute="_get_shoes_stock_move_pair_count"
    )

    assortment_pair_ids = fields.One2many('assortment.pair','sm_id', string='Assortment pairs')