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
    shoes_qty_available = fields.Float(
        string='Disponible',
        related='product_id.qty_available',
        digits='Product Unit of Measure',
        readonly=True,
    )
    shoes_qty_forecasted = fields.Float(
        string='Pronosticado',
        related='product_id.virtual_available',
        digits='Product Unit of Measure',
        readonly=True,
    )
    is_for_own_stock = fields.Boolean(
        string='Para stock propio',
        compute='_compute_is_for_own_stock',
        store=True,
        help="True si la recepción es para stock de la empresa (sin pedido de venta "
             "o con pedido de venta cuyo cliente es la propia empresa).",
    )

    @api.depends('procure_method')
    def _compute_is_mto(self):
        for move in self:
            move.is_mto = move.procure_method == 'make_to_order'

    @api.depends('move_line_ids.quantity')
    def _compute_shoes_reserved_qty(self):
        for move in self:
            move.shoes_reserved_qty = sum(move.move_line_ids.mapped('quantity'))

    @api.depends('sale_id', 'sale_id.partner_id', 'company_id', 'company_id.partner_id')
    def _compute_is_for_own_stock(self):
        for move in self:
            if not move.sale_id:
                move.is_for_own_stock = True
            else:
                move.is_for_own_stock = (
                    move.sale_id.partner_id == move.company_id.partner_id
                )
