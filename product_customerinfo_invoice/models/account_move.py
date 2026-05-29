# Copyright 2024 Punt Sistemes SL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    partner_show_customer_code = fields.Boolean(
        compute="_compute_partner_show_customer_code"
    )

    def _compute_partner_show_customer_code(self):
        """The field is used to show/hide the customer code in the invoice."""
        for rec in self:
            rec.partner_show_customer_code = rec.is_sale_document()
