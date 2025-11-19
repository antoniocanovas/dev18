# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    sale_type_id = fields.Many2one(
        'sale.order.type',
        string='Sale Type',
        related='order_id.type_id',
        store=True,
        readonly=True
    )

    shoes_pair_delivered_qty = fields.Float(
        string="Sent pairs",
        compute="_compute_shoes_pair_quantities",
        store=True,
        digits='Product Unit of Measure'
    )

    delivery_pending_qty = fields.Float(
        string="Delivery pending",
        compute="_compute_delivery_pending_qty",
        store=True,
        digits='Product Unit of Measure'
    )

    shoes_pair_delivery_pending_qty = fields.Float(
        string="Pending pairs",
        compute="_compute_shoes_pair_quantities",
        store=True,
        digits='Product Unit of Measure'
    )

    cancelled_qty = fields.Float(
        string="Cancelled Qty",
        compute="_compute_cancelled_qty",
        store=True,
        digits='Product Unit of Measure'
    )

    shoes_pair_cancelled_qty = fields.Float(
        string="Cancelled pairs",
        compute="_compute_shoes_pair_quantities",
        store=True,
        digits='Product Unit of Measure'
    )

    reserved_qty = fields.Float(
        string="Reserved",
        compute="_compute_reserved_qty",
        store=True,
        digits='Product Unit of Measure'
    )

    shoes_pair_reserved_qty = fields.Float(
        string="Reserved pairs",
        compute="_compute_shoes_pair_quantities",
        store=True,
        digits='Product Unit of Measure'
    )

    @api.depends('qty_delivered', 'product_uom_qty', 'pairs_count', 'move_ids.product_uom_qty', 'move_ids.state', 'move_ids.reserved_availability')
    def _compute_shoes_pair_quantities(self):
        """
        Calcula las cantidades en pares para entregados, pendientes, cancelados y reservados.
        """
        for record in self:
            pairs_factor = record.pairs_count / record.product_uom_qty if record.product_uom_qty else 0
            
            # Pares entregados
            record.shoes_pair_delivered_qty = record.qty_delivered * pairs_factor

            # Pares pendientes
            pending_qty = sum(move.product_uom_qty for move in record.move_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            record.shoes_pair_delivery_pending_qty = pending_qty * pairs_factor

            # Pares cancelados
            record.shoes_pair_cancelled_qty = (record.product_uom_qty - record.qty_delivered - pending_qty) * pairs_factor

            # Pares reservados
            reserved_qty = sum(move.reserved_availability for move in record.move_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
            record.shoes_pair_reserved_qty = reserved_qty * pairs_factor

    @api.depends('move_ids.product_uom_qty', 'move_ids.state')
    def _compute_delivery_pending_qty(self):
        """
        Calcula la cantidad pendiente de entrega (en unidades) sumando los movimientos
        de stock que no están 'hechos' o 'cancelados'.
        """
        for record in self:
            record.delivery_pending_qty = sum(move.product_uom_qty for move in record.move_ids.filtered(lambda m: m.state not in ('done', 'cancel')))

    @api.depends('product_uom_qty', 'qty_delivered', 'delivery_pending_qty')
    def _compute_cancelled_qty(self):
        """
        Calcula la cantidad cancelada (en unidades) basándose en la cantidad pedida,
        entregada y pendiente.
        """
        for record in self:
            record.cancelled_qty = record.product_uom_qty - record.qty_delivered - record.delivery_pending_qty

    @api.depends('move_ids.reserved_availability', 'move_ids.state')
    def _compute_reserved_qty(self):
        """
        Calcula la cantidad reservada (en unidades) sumando la disponibilidad reservada
        de todos los movimientos de stock que no estén 'hechos' o 'cancelados'.
        """
        for record in self:
            record.reserved_qty = sum(move.reserved_availability for move in record.move_ids.filtered(lambda m: m.state not in ('done', 'cancel')))
