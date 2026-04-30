# Copyright 2024 Punt Sistemes SL

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    type_id = fields.Many2one(
        string="Shipping Mark",
    )

    def create_lots_for_sale_order(self):
        self.ensure_one()
        return super(SaleOrder, self.with_context(
            shippingmark_id=self.type_id.id or False,
        )).create_lots_for_sale_order()
