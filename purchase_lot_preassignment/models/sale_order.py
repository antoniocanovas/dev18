# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _get_qty_to_purchase(self, sol, qty_sold=None):
        """
        Returns the quantity to purchase for a sale order line.
        Base implementation: always buy the full sold qty.
        Override in submodules for stock-aware net calculation.
        """
        if qty_sold is None:
            qty_sold = sol.product_uom_qty
        return qty_sold

    def action_cancel(self):
        # Eliminar líneas de compra en borrador vinculadas a líneas de este pedido
        draft_pols = self.env["purchase.order.line"]
        for order in self:
            for line in order.order_line:
                pol = line.purchase_line_id
                if pol and pol.order_id.state == "draft":
                    draft_pols |= pol
        if draft_pols:
            draft_pols.unlink()

        # Limpiar antes: evita que lotes creados durante el cancel queden huérfanos
        for order in self:
            order._delete_unused_lots()
        result = super().action_cancel()
        # Limpiar después: por si la acción automática recreó lotes durante el super
        for order in self:
            order._delete_unused_lots()
        return result

    def action_draft(self):
        for order in self:
            order._delete_unused_lots()
        result = super().action_draft()
        return result

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
        Limpia los lotes sin movimientos activos antes de recrearlos para que
        cada confirmación parta de una lista limpia.
        """
        self.ensure_one()
        if self.env.context.get("skip_lot_creation"):
            return
        if not (self.id and self.order_line and self.state == "sale"):
            return

        self._delete_unused_lots()

        base_name = self.name

        purchase_all = self.company_id.purchase_all_sale
        serial_counter = 1
        for li in self.order_line:
            product = li.product_id
            if product.tracking not in ("lot", "serial"):
                continue
            if purchase_all or li.product_custom_attribute_value_ids:
                quantity = int(li.product_uom_qty)
            elif li.purchase_line_id:
                quantity = int(li.purchase_line_id.product_qty)
            else:
                # Nothing to buy for this line, no lots needed
                continue
            # Red de seguridad: si existe línea de compra con menor cantidad,
            # nunca crear más lotes que unidades realmente compradas
            if li.purchase_line_id:
                quantity = min(quantity, int(li.purchase_line_id.product_qty))
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
