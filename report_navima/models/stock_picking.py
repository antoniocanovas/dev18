# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from typing import Any

from odoo import models  # type: ignore


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def get_packing_list_size_data(self) -> dict[str, Any]:
        """
        Prepara los datos de tallas para el informe packing list.
        Retorna un diccionario con:
        - all_sizes: lista ordenada de todas las tallas únicas
        - lot_data: lista de diccionarios con info de cada lote y sus cantidades
         por talla
        """
        # Obtener todos los move_lines con lotes
        move_lines = self.move_line_ids.filtered(lambda ml: ml.lot_id)

        # Conjunto para recoger todas las tallas únicas
        all_sizes_set = set()
        lot_data_list = []

        for move_line in move_lines:
            lot = move_line.lot_id

            # Obtener el brand desde la línea de compra o venta
            brand = ""
            stock_move = move_line.move_id

            # Obtener product_brand_id del producto
            product_brand = (
                move_line.product_id.product_brand_id.name
                if move_line.product_id.product_brand_id
                else ""
            )

            if stock_move:
                # Intentar obtener desde línea de compra
                if (
                    stock_move.purchase_line_id
                    and stock_move.purchase_line_id.pnt_sale_type_id
                ):
                    brand_record = stock_move.purchase_line_id.pnt_sale_type_id
                    if brand_record.id != 1:
                        # Combinar product_brand con pnt_sale_type
                        if product_brand:
                            brand = f"{product_brand} - {brand_record.name}"
                        else:
                            brand = brand_record.name
                # Si no, intentar obtener desde línea de venta
                elif (
                    stock_move.sale_line_id and stock_move.sale_line_id.order_id.type_id
                ):
                    brand_record = stock_move.sale_line_id.order_id.type_id
                    if brand_record.id != 1:
                        # Combinar product_brand con type_id
                        if product_brand:
                            brand = f"{product_brand} - {brand_record.name}"
                        else:
                            brand = brand_record.name

            # Inicializar diccionario para este lote
            lot_info = {
                "move_line": move_line,
                "lot_name": lot.name,
                "order": self.origin or "",
                "nrb": move_line.product_id.assortment_attribute_id.name
                if move_line.product_id.assortment_attribute_id
                else "",
                "item": move_line.product_id.shoes_model_material
                if move_line.product_id.shoes_model_material
                else "",
                "color": move_line.product_id.color_value_id.name
                if move_line.product_id.color_value_id
                else "",
                "quantity": move_line.quantity,
                "brand": brand,
                "sizes": {},  # Diccionario de talla -> cantidad
                "total_pairs": 0,  # Total de pares (suma de todas las tallas)
            }

            # Parsear assortment_pair del lote
            if lot.assortment_pair:
                parts = lot.assortment_pair.split(";")
                if len(parts) == 3:
                    sizes_list = [s.strip() for s in parts[0].split(",") if s.strip()]
                    quantities_list = [
                        q.strip() for q in parts[1].split(",") if q.strip()
                    ]

                    # Mapear talla -> cantidad
                    for i, size in enumerate(sizes_list):
                        if i < len(quantities_list):
                            try:
                                qty = int(quantities_list[i])
                                lot_info["sizes"][size] = qty
                                lot_info["total_pairs"] += qty
                                all_sizes_set.add(size)
                            except ValueError:
                                pass

            lot_data_list.append(lot_info)

        # Convertir set de tallas a lista ordenada
        all_sizes = sorted(
            all_sizes_set,
            key=lambda x: float(x) if x.replace(".", "", 1).isdigit() else x,
        )

        return {"all_sizes": all_sizes, "lot_data": lot_data_list}
