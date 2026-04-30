# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    purchase_all_sale = fields.Boolean(
        "Purchase all sold",
        store=True,
        default=True,
        help="If disabled, only purchase the net quantity needed: "
             "sold qty minus available stock (respecting exclusive shippingmarks) "
             "minus free incoming stock not linked to any sale order.",
    )
