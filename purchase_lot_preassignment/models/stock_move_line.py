# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    def _reserve_lot_for_sale_order(self):
        """
        Reserva el lote de la recepción de compra para el pedido de venta
         correspondiente.
        Elimina reservas previas del mismo lote en otros pedidos para evitar duplicados.

        - Para RECEPCIONES (incoming): Crea automáticamente la reserva en el
         picking de salida
        - Para SALIDAS (outgoing): Limpia reservas duplicadas cuando se modifican
         manualmente los lotes
        """
        self.ensure_one()

        lot = self.lot_id
        product = self.product_id
        picking_type = self.picking_id.picking_type_id.code  # noqa: F841

        # CASO 1: PICKING DE SALIDA - Solo limpiar duplicados

        # Buscar reservas duplicadas de este lote en OTROS movimientos
        duplicate_lines = self.env["stock.move.line"].search(
            [
                ("id", "!=", self.id),  # Excluir la línea actual
                ("lot_id", "=", lot.id),
                ("product_id", "=", product.id),
                (
                    "state",
                    "in",
                    ["confirmed", "waiting", "partially_available", "assigned"],
                ),
            ]
        )

        if duplicate_lines:
            duplicate_lines.unlink()

        for record in self:
            lot = record.lot_id
            product = record.product_id
            so_name = lot.ref  # Obtenemos la referencia del Lote/SN.

            if so_name:
                # Buscamos el pedido de venta que coincida con la referencia.
                sale_order = self.env["sale.order"].search(
                    [("name", "=", so_name)], limit=1
                )

                if sale_order:
                    # Buscamos el movimiento de entrega (salida) asociado a esa
                    # venta que aún esté pendiente.
                    target_move = self.env["stock.move"].search(
                        [
                            ("sale_line_id.order_id", "=", sale_order.id),
                            ("product_id", "=", product.id),
                            ("picking_type_id.code", "=", "outgoing"),
                            (
                                "state",
                                "in",
                                [
                                    "confirmed",
                                    "waiting",
                                    "partially_available",
                                    "assigned",
                                ],
                            ),
                        ],
                        limit=1,
                    )

                    if target_move:
                        qty_to_reserve = 0
                        # --- Lógica de Trazabilidad ---
                        # Caso 1: Trazabilidad por Número de Serie
                        if product.tracking == "serial":
                            # Para series, solo reservamos si no hay ya una reserva
                            # para este lote/serie.
                            # Esto evita duplicados en caso de que la acción
                            # se ejecute varias veces.
                            already_reserved = self.env["stock.move.line"].search_count(
                                [
                                    ("move_id", "=", target_move.id),
                                    ("lot_id", "=", lot.id),
                                ]
                            )
                            if not already_reserved:
                                qty_to_reserve = 1
                        # Caso 2: Trazabilidad por Lote
                        elif product.tracking == "lot":
                            qty_received_in_lot = record.quantity
                            # Calculamos lo ya reservado para este movimiento de venta.
                            reserved_qty = sum(
                                target_move.move_line_ids.mapped("quantity")
                            )
                            # Calculamos lo que realmente falta por reservar.
                            qty_needed_for_sale = (
                                target_move.product_uom_qty - reserved_qty
                            )
                            # Asignamos la cantidad más pequeña entre lo recién
                            # recibido y lo que aún falta.
                            qty_to_reserve = min(
                                qty_received_in_lot, qty_needed_for_sale
                            )

                        # --- Fin de la Lógica ---

                        # Solo creamos la reserva si la cantidad calculada
                        # es mayor que cero.
                        if qty_to_reserve > 0:
                            self.env["stock.move.line"].create(
                                {
                                    "move_id": target_move.id,
                                    "picking_id": target_move.picking_id.id,
                                    "product_id": product.id,
                                    "quantity": qty_to_reserve,
                                    "product_uom_id": product.uom_id.id,
                                    "lot_id": lot.id,
                                    "location_id": record.location_dest_id.id,
                                    "location_dest_id": target_move.location_dest_id.id,
                                }
                            )
