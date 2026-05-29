# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = "product.category"

    shoes_assortmentpairs_qty = fields.Integer("Assortment pairs qty", default=0)
