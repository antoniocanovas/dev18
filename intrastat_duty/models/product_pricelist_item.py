# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from typing import Any

from odoo import fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    base = fields.Selection(
        selection_add=[
            ("estimated_landed_cost", "Estimated landed cost"),
        ],
        ondelete={"estimated_landed_cost": "set default"},
    )

    def _compute_base_price(
        self,
        product: Any,
        quantity: float,
        uom: Any | None,
        date: Any,
        currency: Any | None,
    ) -> float:
        """Override to handle estimated_landed_cost base"""
        if self.base == "estimated_landed_cost":
            # Convertir a la unidad de medida correcta si es necesario
            if uom and uom != product.uom_id:
                price = product.uom_id._compute_price(
                    product.estimated_landed_cost, uom
                )
            else:
                price = product.estimated_landed_cost

            # Convertir a la moneda de la tarifa si es necesario
            if currency and product.currency_id != currency:
                price = product.currency_id._convert(
                    price, currency, self.env.company, date, round=False
                )
            return price

        # Para otros tipos de base, llamar al método original
        return super()._compute_base_price(product, quantity, uom, date, currency)
