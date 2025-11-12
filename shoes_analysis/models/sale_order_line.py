# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Pares suministrados desde pedido de venta:
    shoes_pair_delivered_qty = fields.Float(
        string="Sent pairs",
        compute="_get_shoes_pair_delivered_qty",
        store=True,
        compute_sudo=True,
        digits='Product Unit of Measure' # Usa la precisión de UoM
    )

    # Unidades pendientes de servir desde el pedido de venta, considerando envíos cancelados:
    delivery_pending_qty = fields.Float(
        string="Delivery pending",
        compute="_get_delivery_pending_qty",
        store=True,
        compute_sudo=True,
        digits='Product Unit of Measure' # Usa la precisión de UoM
    )

    # PARES pendientes de servir desde el pedido de venta, considerando envíos cancelados:
    shoes_pair_delivery_pending_qty = fields.Float(
        string="Pending pairs",
        compute="_get_shoes_pair_delivery_pending_qty",
        store=True,
        compute_sudo=True,
        digits='Product Unit of Measure' # Usa la precisión de UoM
    )

    # Unidades canceladas (vendidos - servidos - pendientes):
    cancelled_qty = fields.Float(
        string="Delivery pending",
        compute="_get_cancelled_qty",
        store=True,
        compute_sudo=True,
        digits='Product Unit of Measure' # Usa la precisión de UoM
    )

    # PARES cancelados (vendidos - servidos - pendientes):
    shoes_pair_cancelled_qty = fields.Float(
        string="Cancelled pairs",
        compute="_get_shoes_pair_cancelled_qty",
        store=True,
        compute_sudo=True,
        digits='Product Unit of Measure' # Usa la precisión de UoM
    )

    # RESERVADOS EN ALBARÁN:
    reserved_qty = fields.Float(
        string="Reserved",
        compute="_get_reserved_qty",
        #store=True,
        compute_sudo=True,
        digits='Product Unit of Measure' # Usa la precisión de UoM
    )

    # PARES RESERVADOS EN ALBARÁN):
    shoes_pair_reserved_qty = fields.Float(
        string="Reserved pairs",
        compute="_get_shoes_pair_reserved_qty",
        #store=True,
        compute_sudo=True,
        digits='Product Unit of Measure' # Usa la precisión de UoM
    )


    # PARES ENTREGADOS:
    @api.depends('qty_delivered')
    def _get_shoes_pair_delivered_qty(self):
        for record in self:
            delivery_pair_qty = 0
            if record.product_id.is_assortment or record.product_id.is_pair:
                delivery_pair_qty += record.qty_delivered * record.pairs_count
            record.shoes_pair_delivered_qty = delivery_pair_qty

    # PENDIENTES:
    @api.depends('move_ids.product_uom_qty')
    def _get_delivery_pending_qty(self):
        for record in self:
            pending_qty = 0
            for move in record.move_ids:
                # Sumamos solo los movimientos que aún se espera procesar
                if move.state not in ('done', 'cancel'):
                    pending_qty += move.product_uom_qty
            record.delivery_pending_qty = pending_qty

    @api.depends('delivery_pending_qty')
    def _get_shoes_pair_delivery_pending_qty(self):
        for record in self:
            pending_pair_qty = 0
            if record.product_id.is_assortment or record.product_id.is_pair:
                pending_pair_qty = record.delivery_pending_qty * record.pairs_count
            record.shoes_pair_delivery_pending_qty = pending_pair_qty

    # CANCELADOS:
    @api.depends('product_uom_qty', 'qty_delivered', 'delivery_pending_qty')
    def _get_cancelled_qty(self):
        for record in self:
            record.cancelled_qty =  (record.product_uom_qty - record.qty_delivered - record.delivery_pending_qty)

    @api.depends('cancelled_qty')
    def _get_shoes_pair_cancelled_qty(self):
        for record in self:
            cancelled_pair_qty = 0
            if record.product_id.is_assortment or record.product_id.is_pair:
                cancelled_pair_qty += record.cancelled_qty * record.pairs_count
            record.shoes_pair_cancelled_qty = cancelled_pair_qty


    # RESERVADOS:
    def _get_reserved_qty(self):
        """
        Calcula la cantidad reservada sumando la disponibilidad reservada
        de todos los movimientos de stock que no estén 'hechos' o 'cancelados'.
        """
        for line in self:
            total = 0
            if line.move_ids.ids and line.state not in ['draft']:
                relevant_moves = line.move_ids.filtered(
                    lambda m: m.state not in ('done', 'cancel')
                )
                total = sum(relevant_moves.mapped('reserved_availability'))
            line.shoes_pair_reserved_qty = total

    def _get_shoes_pair_reserved_qty(self):
        for record in self:
            reserved_pair_qty = 0
            if record.product_id.is_assortment or record.product_id.is_pair:
                reserved_pair_qty = record.reserved_qty * record.pairs_count
            record.shoes_pair_reserved_qty = reserved_pair_qty

