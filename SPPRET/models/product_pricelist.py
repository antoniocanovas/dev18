from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    retail_pricelist_id = fields.Many2one(
        "product.pricelist",
        string="Retail Pricelist",
        help="Reference pricelist for retail prices (RRP/PVP)",
    )
