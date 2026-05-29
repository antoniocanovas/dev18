from odoo import fields, models


class SaleOrderDiscount(models.TransientModel):
    _inherit = "sale.order.discount"

    discount2 = fields.Float(string="Discount 2 (%)", digits="Discount", default=0.0)
    discount3 = fields.Float(string="Discount 3 (%)", digits="Discount", default=0.0)

    def action_apply_discount(self):
        self.ensure_one()
        if self.discount_type != "sol_discount":
            return super().action_apply_discount()
        self = self.with_company(self.company_id)
        # discount_percentage is stored as 0-1 fraction (existing field, widget="percentage").
        # discount2/discount3 are stored as 0-100 to match sale.order.line fields directly.
        self.sale_order_id.order_line.write(
            {
                "discount": self.discount_percentage * 100,
                "discount2": self.discount2,
                "discount3": self.discount3,
            }
        )
