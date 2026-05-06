import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def _get_pricelist_price(self):
        self.ensure_one()
        # Obtenemos precio original
        original_price = super()._get_pricelist_price()

        # Por defecto devolvemos el original
        pricelist_price = original_price

        if self.product_id.is_assortment:
            tmpl = self.product_id.product_tmpl_single_id
            # Tomamos el primer variant como recordset
            product_variant = tmpl.product_variant_ids[:1]
            if product_variant:
                price_pair = self.order_id.pricelist_id._get_product_price(
                    product=product_variant,
                    quantity=1,
                    date=self.order_id.date_order,
                    uom_id=product_variant.uom_id.id,
                )
                if self.product_uom_qty:
                    pricelist_price = price_pair * (self.pairs_count / self.product_uom_qty)
                else:
                    pricelist_price = 0.0

        return pricelist_price
