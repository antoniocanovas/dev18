# Copyright 2024 Punt Sistemes SL

from odoo import models


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _gather(self, product_id, location_id, lot_id=None, package_id=None,
                owner_id=None, strict=False, **kwargs):
        quants = super()._gather(
            product_id, location_id, lot_id=lot_id, package_id=package_id,
            owner_id=owner_id, strict=strict, **kwargs
        )
        allowed_sm_ids = self.env.context.get("shoes_allowed_shippingmark_ids")
        # Only filter when the context explicitly carries a non-empty SM list
        # and the product is an assortment (lots carry shippingmark_id)
        if allowed_sm_ids and product_id.is_assortment:
            quants = quants.filtered(
                lambda q: q.lot_id
                and q.lot_id.shippingmark_id.id in allowed_sm_ids
            )
        return quants
