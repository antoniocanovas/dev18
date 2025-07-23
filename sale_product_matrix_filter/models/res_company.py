# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    sale_filter_attribute_id = fields.Many2one(
        "product.attribute", string="Filter attribute", store=True
    )

    default_sale_filter_value_ids = fields.Many2many(
        "product.attribute.value",
        'res_company_attribute_value_rel',
        'company_id',
        'attribute_value_id',
        string="Default filter attributes",
        store=True
    )
