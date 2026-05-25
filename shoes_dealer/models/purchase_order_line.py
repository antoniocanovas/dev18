# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        orders_to_sync = self.env["purchase.order"]
        for line in lines:
            if line.product_id.is_assortment:
                orders_to_sync |= line.order_id
        for order in orders_to_sync:
            order.create_lots_for_purchase_order()
        return lines

    def write(self, vals):
        orders_to_sync = self.env["purchase.order"]
        if "product_qty" in vals:
            for line in self:
                if line.product_id.is_assortment:
                    orders_to_sync |= line.order_id
        result = super().write(vals)
        for order in orders_to_sync:
            order.create_lots_for_purchase_order()
        return result

    def unlink(self):
        orders_to_sync = self.filtered(
            lambda l: l.product_id.is_assortment
        ).mapped("order_id")
        result = super().unlink()
        for order in orders_to_sync:
            order.create_lots_for_purchase_order()
        return result

    # Comercialmente en cada pedido quieren saber cuántos pares se han comprado:
    @api.depends("product_id", "product_qty")
    def _get_shoes_purchase_line_pair_count(self) -> None:
        for record in self:
            record["pairs_count"] = record.product_id.pairs_count * record.product_qty

    pairs_count = fields.Integer(
        "Pairs", store=True, compute="_get_shoes_purchase_line_pair_count"
    )

    # Precio por par según tarifa:
    @api.depends("product_id", "price_unit")
    def _get_shoes_pair_price(self) -> None:
        """
        Compute the price per pair in the purchase order line.
        """
        for record in self:
            total = 0
            if record.pairs_count != 0:
                total = record.price_subtotal / record.pairs_count
            record["pair_price"] = total

    pair_price = fields.Float("Pair price", store=True, compute="_get_shoes_pair_price")

