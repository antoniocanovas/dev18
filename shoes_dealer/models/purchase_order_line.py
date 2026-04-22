# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    # Comercialmente en cada pedido quieren saber cuántos pares se han comprado:
    @api.depends("product_id", "product_qty", "sale_line_id.custom_assortment_pairs")
    def _get_shoes_purchase_line_pair_count(self) -> None:
        """
        Compute the number of pairs in the purchase order line.
        """
        for record in self:
            sol = record.sale_line_id
            if sol and sol.product_custom_attribute_value_ids:
                # Surtido personalizado (texto libre): pares por unidad desde la SOL
                pairs_per_unit = sol.custom_assortment_pairs
            else:
                # Surtido normal o compra directa: pares por unidad desde el producto
                pairs_per_unit = record.product_id.pairs_count
            record["pairs_count"] = pairs_per_unit * record.product_qty

    pairs_count = fields.Integer(
        "Pairs", store=True, compute="_get_shoes_purchase_line_pair_count"
    )

    # Precio por par según tarifa:
    @api.depends("product_id", "price_unit")
    def _get_shoes_pair_price(self) -> None:
        """
        Compute the price per pair in the purchase order line.
        """
        for record in self:
            total = 0
            if record.pairs_count != 0:
                total = record.price_subtotal / record.pairs_count
            record["pair_price"] = total

    pair_price = fields.Float("Pair price", store=True, compute="_get_shoes_pair_price")

    # Campo de texto para escribir los valores personalizados de tallas
    # y cantidad, desde el pedido de venta:
    assortment_pair_id = fields.Many2one(
        "product.attribute.custom.value", string="Assortment pair", store=True
    )
