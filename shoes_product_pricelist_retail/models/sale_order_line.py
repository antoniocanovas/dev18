from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "product_id",
        "product_id.is_assortment",
        "pairs_count",
        "order_id.pricelist_id",
        "order_id.pricelist_id.retail_pricelist_id",
        "product_uom",
        "product_uom_qty",
    )
    def _compute_retail_price(self):
        """Override retail price calculation for assortment products"""
        super()._compute_retail_price()
        for line in self:
            if line.product_id and line.product_id.is_assortment and line.pairs_count and line.product_uom_qty:
                line.retail_price = line.retail_price / (line.pairs_count / line.product_uom_qty)

    @api.onchange("product_id", "pairs_count")
    def _onchange_product_retail_price(self):
        """Override onchange to include pairs_count"""
        super()._onchange_product_retail_price()
        if self.product_id and self.product_id.is_assortment and self.pairs_count and self.product_uom_qty:
            self.retail_price = self.retail_price / (self.pairs_count / self.product_uom_qty)
