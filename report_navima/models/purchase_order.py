from typing import Any

from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    shoes_pair_line_ids = fields.Many2many(
        "purchase.line.shoes.pair.line",
        compute="_compute_shoes_pair_line_ids",
        string="Shoes Pair Lines",
        help="All shoes pair lines from all order lines in this purchase order",
    )
    shoes_pair_line_count = fields.Integer(
        string="Pair Lines Count",
        compute="_compute_shoes_pair_line_ids",
        help="Number of shoes pair lines in this purchase order",
    )

    @api.depends("order_line", "order_line.shoes_pair_line_ids")
    def _compute_shoes_pair_line_ids(self):
        """Compute all shoes pair lines from order lines."""
        for order in self:
            pair_lines = order.order_line.mapped("shoes_pair_line_ids")
            order.shoes_pair_line_ids = pair_lines
            order.shoes_pair_line_count = len(pair_lines)

    def action_view_shoes_pair_lines(self) -> dict[str, Any]:
        """Open list view with all shoes pair lines for this purchase order."""
        self.ensure_one()

        return {
            "name": f"Pares de Zapatos - {self.name}",
            "type": "ir.actions.act_window",
            "res_model": "purchase.line.shoes.pair.line",
            "view_mode": "list,pivot,graph",
            "domain": [("order_id", "=", self.id)],
            "context": {
                "default_order_id": self.id,
                "search_default_group_by_model": 1,
                "search_default_group_by_color": 1,
                "create": False,
            },
            "target": "current",
        }
