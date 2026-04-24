# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _delete_unused_lots(self):
        """
        Elimina todos los lotes asociados a este pedido de venta (lot.ref = SO name)
        que no tengan stock.move.line activos (no cancelados).
        """
        self.ensure_one()
        lots = self.env["stock.lot"].search([("ref", "=", self.name)])
        safe_to_delete = lots.filtered(
            lambda l: not self.env["stock.move.line"].search_count(
                [("lot_id", "=", l.id), ("state", "not in", ["cancel"])]
            )
        )
        safe_to_delete.unlink()

    def create_lots_for_sale_order(self):
        """
        Crea los lotes para todas las líneas del pedido de venta usando un contador
        global incremental, evitando colisiones entre líneas del mismo producto.
        Solo crea los lotes que no existan aún.
        """
        self.ensure_one()
        if not (self.id and self.order_line and self.state == "sale"):
            return

        name_parts = []
        if self.client_order_ref:
            name_parts.append(self.client_order_ref)
        name_parts.append(self.name)
        base_name = "-".join(name_parts)

        serial_counter = 1
        for li in self.order_line:
            product = li.product_id
            if product.tracking not in ("lot", "serial"):
                continue
            quantity = int(li.product_uom_qty)
            if quantity < 1:
                continue
            if product.tracking == "serial":
                for _ in range(quantity):
                    final_name = "%s-%03d" % (base_name, serial_counter)
                    existing = self.env["stock.lot"].search(
                        [
                            ("product_id", "=", product.id),
                            ("name", "=", final_name),
                            ("company_id", "=", self.company_id.id),
                        ],
                        limit=1,
                    )
                    if not existing:
                        self.env["stock.lot"].create(
                            {
                                "name": final_name,
                                "product_id": product.id,
                                "ref": self.name,
                                "company_id": self.company_id.id,
                            }
                        )
                    serial_counter += 1
            else:  # lot tracking: un lote por línea, sin secuencia
                final_name = base_name
                existing = self.env["stock.lot"].search(
                    [
                        ("product_id", "=", product.id),
                        ("name", "=", final_name),
                        ("company_id", "=", self.company_id.id),
                    ],
                    limit=1,
                )
                if not existing:
                    self.env["stock.lot"].create(
                        {
                            "name": final_name,
                            "product_id": product.id,
                            "ref": self.name,
                            "company_id": self.company_id.id,
                        }
                    )

    def action_view_associated_lots(self) -> dict:
        """
        Abre un wizard para ver los lotes asociados a este pedido de venta.
        """
        self.ensure_one()

        return {
            "name": "Lotes Asociados",
            "type": "ir.actions.act_window",
            "res_model": "sale.lot.view.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_sale_order_id": self.id,
            },
        }
