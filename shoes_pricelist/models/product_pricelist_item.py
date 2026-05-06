# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = ["product.pricelist.item"]

    shoes_campaign_id = fields.Many2one(
        "project.project",
        string="Campaign",
        related="product_tmpl_id.shoes_campaign_id",
    )

    pnt_visible_by_campaign = fields.Boolean(
        string="Visible by Campaign Filter",
        compute="_compute_pnt_visible_by_campaign",
        store=True,
        help="Indica si la línea debe ser visible según el filtro de campañas de la tarifa",
    )

    @api.depends(
        "pricelist_id.pnt_campaign_filter_ids",
        "product_tmpl_id.shoes_campaign_ids",
        "product_tmpl_id.pnt_has_campaigns",
    )
    def _compute_pnt_visible_by_campaign(self) -> None:
        """
        Calcula si la línea debe ser visible según el filtro de campañas.

        Lógica:
        - Si la tarifa NO tiene campañas filtro: visible = True
        - Si la tarifa tiene campañas filtro:
            - Si el producto NO tiene campañas: visible = True
            - Si el producto tiene campañas: visible = (hay intersección)
        """
        for record in self:
            pricelist_campaigns = record.pricelist_id.pnt_campaign_filter_ids
            product_campaigns = record.product_tmpl_id.shoes_campaign_ids

            # Sin filtro de campaña en la tarifa, mostrar todas las líneas
            if not pricelist_campaigns:
                record.pnt_visible_by_campaign = True
                continue

            # Producto sin campañas, siempre visible
            if not record.product_tmpl_id.pnt_has_campaigns:
                record.pnt_visible_by_campaign = True
                continue

            # Producto con campañas: visible si hay intersección
            record.pnt_visible_by_campaign = bool(
                pricelist_campaigns & product_campaigns
            )
