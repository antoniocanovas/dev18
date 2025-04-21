# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    fsc_dimension_attribute_id = fields.Many2one(
        "product.attribute",
        string="Dimension attribute",
        store=True,
        help="Internal attribute to group products",
    )
    fsc_quality_attribute_id = fields.Many2one(
        "product.attribute",
        string="Quality attribute",
        store=True,
        help="Internal attribute to group products",
    )
