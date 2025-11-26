from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "product_id",
        "product_id.is_assortment",
        "product_id.product_tmpl_single_id",
        "product_id.product_tmpl_single_id.product_variant_ids",
        "order_id.pricelist_id",
        "order_id.pricelist_id.retail_pricelist_id",
        "order_id.date_order",
        "product_uom",
        "product_uom_qty",
    )
    def _compute_retail_price(self):
        """Override retail price calculation for assortment products"""
        super()._compute_retail_price()
        for line in self.filtered(
            lambda l: l.order_id.pricelist_id.retail_pricelist_id
            and l.product_id
            and l.product_id.is_assortment
            and l.product_id.product_tmpl_single_id
            and l.product_id.product_tmpl_single_id.product_variant_ids
        ):
            pricelist = line.order_id.pricelist_id.retail_pricelist_id
            product_variant = (
                line.product_id.product_tmpl_single_id.product_variant_ids[0]
            )
            price = pricelist._get_product_price(
                product=product_variant,
                quantity=1.0,
                partner=line.order_id.partner_id,
                uom=line.product_uom,
                date=line.order_id.date_order,
            )
            line.retail_price = pricelist.currency_id.round(price)
