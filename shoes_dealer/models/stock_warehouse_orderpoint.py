# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api


class StockWarehouseOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    product_brand_id = fields.Many2one(
        string="Product brand",
        related="product_id.product_brand_id",
        store=True,
        readonly=True,
    )
    shoes_campaign_id = fields.Many2one(
        string="Campaign",
        related="product_id.shoes_campaign_id",
        store=True,
        readonly=True,
    )
    is_assortment = fields.Boolean(
        string="Assortment",
        related="product_id.is_assortment",
        readonly=True,
    )
    assortment_filter = fields.Boolean(
        string="Is Assortment",
        related="is_assortment",
        store=True,
        readonly=True,
    )
    product_image = fields.Binary(
        string="Photo",
        related="product_id.image_1024",
        depends=["product_id"],
        readonly=True,
    )
