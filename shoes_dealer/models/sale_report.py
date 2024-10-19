# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api


class SaleReport(models.Model):
    _inherit = "sale.report"

    campaign_id = fields.Many2one("utm.campaign", "Marketing Campaign", readonly=True)

    color_attribute_id = fields.Many2one(
        "product.attribute.value",
        string="Color",
    )

    size_attribute_id = fields.Many2one(
        "product.attribute.value",
        string="Size",
    )

    state_id = fields.Many2one("res.country.state", "Customer State", readonly=True)

    @api.depends("product_id")
    def _get_shoes_pair_count(self):
        for record in self:
            pairs_count = 1
            if record.product_id.pairs_count:
                pairs_count = record.product_id.pairs_count
            record["pairs_count"] = pairs_count * record.product_uom_qty

    pairs_count = fields.Integer("Pairs", store=True, compute="_get_shoes_pair_count")

    shoes_campaign_id = fields.Many2one("project.project", string="Shoes Campaign")
    manufacturer_id = fields.Many2one(
        string="Manufacturer",
        comodel_name="res.partner",
    )

    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res["color_attribute_id"] = "p.color_attribute_id"
        res["size_attribute_id"] = "p.size_attribute_id"
        res["shoes_campaign_id"] = "s.shoes_campaign_id"
        res["state_id"] = "partner.state_id"
        res["pairs_count"] = "l.pairs_count"
        res["manufacturer_id"] = "t.manufacturer_id"
        return res

    def _group_by_sale(self):
        res = super()._group_by_sale()
        """
        res +=,
         p.color_attribute_id,
         p.size_attribute_id,
         s.shoes_campaign_id,
         partner.state_id,
         t.manufacturer_id,
              l.pairs_count"""
        return res
