from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discount1 = fields.Float(string="Discount 1 (%)", digits="Discount")
    discount2 = fields.Float(string="Discount 2 (%)", digits="Discount")
    discount3 = fields.Float(string="Discount 3 (%)", digits="Discount")

    @api.onchange("partner_id")
    def _onchange_partner_id_triple_discount(self):
        if self.partner_id:
            self.discount1 = self.partner_id.discount1
            self.discount2 = self.partner_id.discount2
            self.discount3 = self.partner_id.discount3

    @api.onchange("grid")
    def _apply_grid(self):
        # _apply_grid calls default_get on sale.order.line without default_order_id
        # in context, so our default_get override cannot inject the order discounts.
        # We fix this by setting the three discounts on truly new lines after super().
        # Note: sale.order.line uses 'discount' (not 'discount1') for the first discount.
        super()._apply_grid()
        if not (self.discount1 or self.discount2 or self.discount3):
            return
        for line in self.order_line:
            if line._origin:
                # Existing persisted line — leave its discounts untouched.
                continue
            if not line.discount and self.discount1:
                line.discount = self.discount1
            if not line.discount2 and self.discount2:
                line.discount2 = self.discount2
            if not line.discount3 and self.discount3:
                line.discount3 = self.discount3
