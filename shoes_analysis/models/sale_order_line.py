# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
from odoo import api, fields, models, _

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # Unidades pendientes de servir desde el pedido de venta, considerando envíos cancelados:
    delivery_pending_qty = fields.Float(
        string="Delivery pending",
        compute="_get_delivery_pending_qty",
    )

    # PARES pendientes de servir desde el pedido de venta, considerando envíos cancelados:
    shoes_pair_delivery_pending_qty = fields.Float(
        string="Delivery pending",
        compute="_get_shoes_pair_delivery_pending_qty",
    )

    def _get_delivery_pending_qty(self):
        for record in self:
            pending_qty = 0
            for move in record.move_ids:
                # Sumamos solo los movimientos que aún se espera procesar
                if move.state not in ('done', 'cancel'):
                    pending_qty += move.product_uom_qty
            record.delivery_pending_qty = pending_qty

    def _get_shoes_pair_delivery_pending_qty(self):
        for record in self:
            pair_qty = 0
            if record.product_id.is_assortment or record.product_id.is_pair:
                pair_qty += record.delivery_pending_qty * record.pairs_count
            record.shoes_pair_delivery_pending_qty = pair_qty
