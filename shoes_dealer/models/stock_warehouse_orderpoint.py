# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    pnt_product_brand_id = fields.Many2one(
        string="Product brand",
        related="product_id.product_brand_id",
        store=True,
        readonly=True,
    )
    pnt_shoes_campaign_id = fields.Many2one(
        string="Campaign",
        related="product_id.shoes_campaign_id",
        store=True,
        readonly=True,
    )
    pnt_is_assortment = fields.Boolean(
        string="Assortment",
        related="product_id.is_assortment",
        readonly=True,
    )
    pnt_assortment_filter = fields.Boolean(
        string="Is Assortment",
        related="pnt_is_assortment",
        store=True,
        readonly=True,
    )
    pnt_product_image = fields.Binary(
        string="Photo",
        related="product_id.image_1024",
        depends=["product_id"],
        readonly=True,
    )
