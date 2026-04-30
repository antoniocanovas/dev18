# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models


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
