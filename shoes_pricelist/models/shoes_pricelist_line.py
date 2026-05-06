# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ShoesPricelist(models.Model):
    _name = "shoes.pricelist.line"
    _description = "Shoes Pricelist Line"

    name = fields.Char(related="product_tmpl_single_id.name", string="Name")
    shoes_pricelist_id = fields.Many2one("shoes.pricelist", string="Pricelist report")
    product_tmpl_single_id = fields.Many2one(
        "product.template", string="Model", domain="[('is_pair','=',True)]"
    )
    pricelist_price = fields.Float("Price")

    image = fields.Binary(related="product_tmpl_single_id.image_1024")
    product_single_price = fields.Float(
        related="product_tmpl_single_id.list_price", string="List price"
    )
    product_standard_price = fields.Monetary(
        related="product_tmpl_single_id.exwork_euro", string="Exwork"
    )
    shoes_campaign_id = fields.Many2one(related="shoes_pricelist_id.shoes_campaign_id")
    pricelist_id = fields.Many2one(related="shoes_pricelist_id.pricelist_id")
    currency_id = fields.Many2one(
        "res.currency",
        store=True,
        default=lambda self: self.env.user.company_id.currency_id,
    )
