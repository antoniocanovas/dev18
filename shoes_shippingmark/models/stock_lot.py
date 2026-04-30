# Copyright 2024 Punt Sistemes SL

from odoo import api, fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    shippingmark_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Shipping Mark",
    )

    @api.model_create_multi
    def create(self, vals_list):
        shippingmark_id = self.env.context.get("shippingmark_id")
        if shippingmark_id:
            for vals in vals_list:
                vals.setdefault("shippingmark_id", shippingmark_id)
        return super().create(vals_list)
