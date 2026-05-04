from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_open_split_wizard(self):
        self.ensure_one()
        return {
            "name": "Dividir pedido de compra",
            "type": "ir.actions.act_window",
            "res_model": "purchase.split.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_purchase_order_id": self.id},
        }
