# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api

class AccountMove(models.Model):
    _inherit = "account.move"

    # Comercialmente en cada pedido quieren saber cuántos pares se han facturado:
    def _get_shoes_pair_count(self):
        for record in self:
            record.pairs_count = sum(li.pairs_count for li in record.invoice_line_ids)

    pairs_count = fields.Integer('Pairs', store=False, compute='_get_shoes_pair_count')
