from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    retail_price = fields.Float(
        string="RRP",
        compute="_compute_retail_price",
        store=True,
        digits="Product Price",
    )

    @api.depends(
        "product_id",
        "order_id.pricelist_id",
        "order_id.pricelist_id.retail_pricelist_id",
        "product_uom",
        "product_uom_qty",
    )
    def _compute_retail_price(self):
        """Calculate retail price from retail pricelist"""
        for line in self:
            retail_price = 0.0
            if (
                line.product_id
                and line.order_id.pricelist_id
                and line.order_id.pricelist_id.retail_pricelist_id
            ):
                retail_pricelist = line.order_id.pricelist_id.retail_pricelist_id
                retail_price = retail_pricelist._get_product_price(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                )
            line.retail_price = retail_price

    @api.onchange("product_id", "product_uom_qty", "product_uom")
    def _onchange_product_retail_price(self):
        """Recalculate retail_price when product, quantity or UoM changes"""
        if (
            self.product_id
            and self.order_id.pricelist_id
            and self.order_id.pricelist_id.retail_pricelist_id
        ):
            retail_pricelist = self.order_id.pricelist_id.retail_pricelist_id
            self.retail_price = retail_pricelist._get_product_price(
                self.product_id,
                self.product_uom_qty or 1.0,
                uom=self.product_uom,
                date=self.order_id.date_order,
            )
        else:
            self.retail_price = 0.0
