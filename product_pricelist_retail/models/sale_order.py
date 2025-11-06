from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.onchange("pricelist_id")
    def _onchange_pricelist_retail_price(self):
        """Recalculate retail_price when pricelist changes"""
        if self.pricelist_id and self.pricelist_id.retail_pricelist_id:
            retail_pricelist = self.pricelist_id.retail_pricelist_id
            for line in self.order_line:
                if line.product_id:
                    line.retail_price = retail_pricelist._get_product_price(
                        line.product_id,
                        line.product_uom_qty or 1.0,
                        uom=line.product_uom,
                        date=self.date_order,
                    )
        else:
            for line in self.order_line:
                line.retail_price = 0.0
