# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def _delete_unused_po_lots(self):
        """
        Elimina los lotes generados para este pedido de compra (lot.ref = PO name)
        que no tengan stock.move.line activos.
        """
        self.ensure_one()
        lots = self.env["stock.lot"].search([("ref", "=", self.name)])
        safe_to_delete = lots.filtered(
            lambda l: not self.env["stock.move.line"].search_count(
                [("lot_id", "=", l.id), ("state", "not in", ["cancel"])]
            )
        )
        safe_to_delete.unlink()

    def create_lots_for_purchase_order(self):
        """
        Crea los lotes para las líneas de compra con tracking lot/serial
        que NO provienen de un pedido de venta (sin sale_line_id).
        Usa el nombre del PO como base con un contador global de tres dígitos.
        Limpia los lotes sin movimientos activos antes de recrearlos.
        """
        self.ensure_one()
        if not self.id or not self.order_line:
            return

        self._delete_unused_po_lots()

        serial_counter = 1
        for line in self.order_line:
            product = line.product_id
            if line.sale_line_id:
                continue
            if product.tracking not in ("lot", "serial"):
                continue
            quantity = int(line.product_qty)
            if quantity < 1:
                continue
            if product.tracking == "serial":
                for _ in range(quantity):
                    final_name = "%s-%03d" % (self.name, serial_counter)
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
            else:  # lot tracking: un lote por línea
                final_name = self.name
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
