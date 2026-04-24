# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_view_associated_lots(self) -> dict:
        """
        Abre un wizard para imprimir etiquetas de los lotes asociados a los
        pedidos de venta relacionados con este pedido de compra.
        """
        self.ensure_one()

        return {
            "name": "Etiquetas de Lotes",
            "type": "ir.actions.act_window",
            "res_model": "purchase.lot.view.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_purchase_order_id": self.id,
            },
        }
