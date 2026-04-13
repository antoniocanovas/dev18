# -*- coding: utf-8 -*-
from odoo import models, fields, api


class StockMoveShoes(models.Model):
    _inherit = 'stock.move'

    warehouse_id = fields.Many2one(
        'stock.warehouse',
        string='Almacén',
        related='location_id.warehouse_id',
        store=True,
        readonly=True,
    )
    is_mto = fields.Boolean(
        string='Bajo Pedido (MTO)',
        compute='_compute_is_mto',
        store=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Cliente',
        related='picking_id.partner_id',
        store=True,
        readonly=True,
    )
    shoes_reserved_qty = fields.Float(
        string='Reservado',
        compute='_compute_shoes_reserved_qty',
        digits='Product Unit of Measure',
    )
    sale_id = fields.Many2one(
        'sale.order',
        string='Pedido de venta',
        related='picking_id.sale_id',
        store=True,
        readonly=True,
    )
    purchase_id = fields.Many2one(
        'purchase.order',
        string='Orden de compra',
        related='picking_id.purchase_id',
        store=True,
        readonly=True,
    )

    @api.depends('procure_method')
    def _compute_is_mto(self):
        for move in self:
            move.is_mto = move.procure_method == 'make_to_order'

    @api.depends('move_line_ids.quantity')
    def _compute_shoes_reserved_qty(self):
        for move in self:
            move.shoes_reserved_qty = sum(move.move_line_ids.mapped('quantity'))
