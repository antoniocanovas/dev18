# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_view_associated_lots(self) -> dict:
        """
        Abre un wizard para ver los lotes asociados a este albarán.
        """
        self.ensure_one()

        return {
            "name": "Lotes Asociados",
            "type": "ir.actions.act_window",
            "res_model": "sale.lot.view.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_picking_id": self.id,
            },
        }
