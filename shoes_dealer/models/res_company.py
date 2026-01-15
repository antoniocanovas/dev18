# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_shoes_company = fields.Boolean("Shoes company", default=True)
    assortment_attribute_id = fields.Many2one(
        "product.attribute", string="Assortment attribute", store=True
    )
    size_attribute_id = fields.Many2one(
        "product.attribute", string="Size attribute", store=True
    )
    color_attribute_id = fields.Many2one(
        "product.attribute", string="Color attribute", store=True
    )
    assortment_prefix = fields.Char("Assortment prefix", store=True)
    single_prefix = fields.Char("Single prefix", store=True)
    single_sale = fields.Boolean("Enable pair sales", store=True, default=False)
    single_purchase = fields.Boolean("Enable pair purchase", store=True, default=False)
    exwork_currency_id = fields.Many2one(
        "res.currency",
        store=True,
        default=lambda self: self.env.user.company_id.currency_id,
    )
    shoes_pair_weight_std = fields.Boolean("Pair standard price", default=True)
    shoes_hs_code_std = fields.Boolean("Standard HS code", default=True)
    shoes_pair_uom_id = fields.Many2one("uom.uom", string="Pair UOM")

    # Shoes tracking:
    shoes_assortment_tracking = fields.Selection(
        [("lot", "Lot"), ("serial", "Serial Number"), ("none", "None")],
        string="Assortment tracking",
        default="lot",
    )
    shoes_pair_tracking = fields.Selection(
        [("lot", "Lot"), ("serial", "Serial Number"), ("none", "None")],
        string="Pair tracking",
        default="none",
    )

    # Auto SYNC options:
    shoes_categ_sync = fields.Boolean(
        "AutoSYNC Category",
        help="Pair and assortment sync accounting category when enabled.",
        default=True,
    )
