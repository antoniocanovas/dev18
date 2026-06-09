# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    shoes_delivery_date_from = fields.Datetime(
        string="Delivery from",
        copy=True,
    )

    internal_user_id = fields.Many2one(
        "res.users",
        related="sale_id.internal_user_id",
        string="Backoffice user",
        store=True,
        readonly=False,
        tracking=True,
        help="Gestor interno de pedidos y envíos",
    )

    partner_country_id = fields.Many2one(
        "res.country",
        related="partner_id.country_id",
        string="Destination country",
        store=True,
        tracking=True,
    )

    salesperson_id = fields.Many2one(
        "res.users",
        related="sale_id.user_id",
        string="Salesperson",
        store=True,
        tracking=True,
    )

    # Comercialmente en cada Albaran quieren saber cuántos pares se han vendido:
    def _get_shoes_pair_count(self):
        for record in self:
            record["pairs_count"] = sum(li.pairs_count for li in record.move_ids_without_package)

    pairs_count = fields.Integer(
        string="Pairs", store=False, compute="_get_shoes_pair_count"
    )

    def _get_shoes_stock_move_packages_count(self):
        for record in self:
            record["packages_count"] = sum(li.quantity for li in record.move_ids_without_package)

    packages_count = fields.Integer(
        "Packages", store=False, compute="_get_shoes_stock_move_packages_count"
    )
