from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        order_id = self.env.context.get("default_order_id")
        if not order_id:
            return defaults
        order = self.env["sale.order"].browse(order_id)
        # sale.order.line uses 'discount' (not 'discount1') for the first discount.
        # Only set it as default if the field is writable (not precomputed by pricelist).
        if "discount" in fields_list:
            defaults.setdefault("discount", order.discount1)
        if "discount2" in fields_list:
            defaults.setdefault("discount2", order.discount2)
        if "discount3" in fields_list:
            defaults.setdefault("discount3", order.discount3)
        return defaults
