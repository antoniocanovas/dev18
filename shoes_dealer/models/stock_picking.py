# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # Comercialmente en cada Albaran quieren saber cuántos pares se han vendido:
    def _get_shoes_pair_count(self):
        for record in self:
            count = 0
            for li in record.move_ids_without_package:
                count += li.pairs_count
            record["pairs_count"] = count

    pairs_count = fields.Integer(
        string="Pairs", store=False, compute="_get_shoes_pair_count"
    )

    def _get_shoes_stock_move_packages_count(self):
        for record in self:
            count = 0
            for li in record.move_ids_without_package:
                count += li.quantity
            record["packages_count"] = count

    packages_count = fields.Integer(
        "Packages", store=False, compute="_get_shoes_stock_move_packages_count"
    )
