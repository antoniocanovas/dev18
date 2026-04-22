# Copyright 2023 Serincloud SL - Ingenieriacloud.com
from typing import Any

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Comercialmente en cada pedido quieren saber cuántos pares se han vendido:
    def _get_shoes_pair_count(self):
        for record in self:
            record["pairs_count"] = sum(li.pairs_count for li in record.order_line)

    pairs_count = fields.Integer(
        string="Pairs", store=False, compute="_get_shoes_pair_count"
    )

    shoes_campaign_id = fields.Many2one(
        "project.project", string="Campaign", store=True, copy=True, tracking=10
    )

    date_cancellation_limit = fields.Date("Cancellation limit")

    @api.depends("shoes_campaign_id")
    def _get_campaign_top_sale(self):
        for record in self:
            models = self.env["product.template"].search(
                [
                    ("shoes_campaign_id", "=", record.shoes_campaign_id.id),
                    ("pairs_sold", ">", 1),
                ],
                limit=10,
            )
            record["campaign_top_ids"] = [(6, 0, models.ids)]

    campaign_top_ids = fields.Many2many(
        "product.template", store=False, compute="_get_campaign_top_sale"
    )

    # Habilita o deshabilita la vista de pares más vendidos en las preferencias
    # de usuario o desde botón en ventas:
    def _get_enabled_top_sales(self):
        self.top_sales = self.env.user.top_sales

    top_sales = fields.Boolean(
        "Top sales", store=False, compute="_get_enabled_top_sales"
    )

    def show_hide_top_sales(self):
        user = self.env.user
        user.top_sales = not user.top_sales

    def _action_confirm(self):
        result = super()._action_confirm()
        self.create_purchase_lines_for_custom_products()
        return result

    def create_purchase_lines_for_custom_products(self):
        for record in self:
            for li in record.order_line:
                # Bug líneas de compra duplicadas:
                if li.product_id.is_assortment and not li.purchase_line_id:
                    vendor = li.product_id.manufacturer_id
                    if not vendor:
                        raise UserError(
                            _(
                                "El producto '%s' no tiene fabricante asignado. "
                                "Asígnalo en la ficha del producto antes de confirmar el pedido.",
                                li.product_id.display_name,
                            )
                        )

                    # Precio por surtido: exwork × pares por unidad de surtido
                    if li.product_custom_attribute_value_ids:
                        pairs_per_unit = li.custom_assortment_pairs
                    else:
                        pairs_per_unit = li.product_id.pairs_count
                    price_unit = li.product_id.exwork * pairs_per_unit

                    draft_purchases = self.env["purchase.order"].search(
                        [("partner_id", "=", vendor.id), ("state", "=", "draft")]
                    )
                    po = draft_purchases[0] if draft_purchases.ids else self.env[
                        "purchase.order"
                    ].create({"partner_id": vendor.id})

                    pol_vals = {
                        "order_id": po.id,
                        "product_id": li.product_id.id,
                        "sale_line_id": li.id,
                        "name": li.name,
                        "price_unit": price_unit,
                        "product_qty": li.product_uom_qty,
                    }
                    if li.product_custom_attribute_value_ids:
                        pol_vals["assortment_pair_id"] = (
                            li.product_custom_attribute_value_ids[0].id
                        )

                    purchase_line = self.env["purchase.order.line"].create(pol_vals)
                    # Indicar en SOL para que no vuelva a crear el pedido:
                    li["purchase_line_id"] = purchase_line.id
