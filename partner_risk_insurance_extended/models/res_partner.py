# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    risk_insurance_end_date = fields.Date(
        string="Insurance Contract End Date",
        help="End date of the financial risk insurance contract with the insurer. "
        "When this date is reached, the insured credit limit is automatically set to zero.",
        copy=False,
        tracking=True,
    )
    risk_credit_limit_before_insurance = fields.Float(
        string="Credit Limit Before Insurance",
        copy=False,
        help="Credit limit saved automatically when insurance is applied, "
        "used to restore the original value when the insurance expires.",
    )
    risk_insurance_expired = fields.Boolean(
        string="Insurance Expired",
        compute="_compute_risk_insurance_expired",
        search="_search_risk_insurance_expired",
    )

    # Computed: True if any risk _include field is active
    risk_remaining_value_include = fields.Boolean(
        string="Include in Risk Monitoring",
        compute="_compute_risk_remaining_value_include",
        store=True,
        help="Automatically enabled when at least one risk type is set to be monitored.",
    )

    # Override risk include fields to set default=True for new records
    risk_sale_order_include = fields.Boolean(default=True)
    risk_invoice_draft_include = fields.Boolean(default=True)
    risk_invoice_open_include = fields.Boolean(default=True)
    risk_invoice_unpaid_include = fields.Boolean(default=True)
    risk_account_amount_include = fields.Boolean(default=True)
    risk_account_amount_unpaid_include = fields.Boolean(default=True)
    risk_payment_return_include = fields.Boolean(default=True)

    # Display field: risk used as "Cobertura X.XX%"
    risk_coverage_display = fields.Char(
        string="Cobertura",
        compute="_compute_risk_coverage_display",
    )

    # Add search methods to enable filtering on computed monetary fields
    risk_sale_order = fields.Monetary(search="_search_risk_sale_order")
    risk_invoice_draft = fields.Monetary(search="_search_risk_invoice_draft")
    risk_invoice_open = fields.Monetary(search="_search_risk_invoice_open")
    risk_invoice_unpaid = fields.Monetary(search="_search_risk_invoice_unpaid")
    risk_account_amount = fields.Monetary(search="_search_risk_account_amount")
    risk_account_amount_unpaid = fields.Monetary(
        search="_search_risk_account_amount_unpaid"
    )
    risk_payment_return = fields.Monetary(search="_search_risk_payment_return")
    risk_amount_exceeded = fields.Monetary(search="_search_risk_amount_exceeded")

    def write(self, vals):
        if "insurance_credit_limit" in vals:
            new_insurance = vals["insurance_credit_limit"]
            for partner in self:
                currently_has_insurance = partner.insurance_credit_limit != 0.0
                setting_insurance = new_insurance != 0.0
                if setting_insurance and not currently_has_insurance:
                    vals_with_snapshot = dict(vals)
                    vals_with_snapshot[
                        "risk_credit_limit_before_insurance"
                    ] = partner.sudo().credit_limit
                    return super().write(vals_with_snapshot)
        return super().write(vals)

    @api.depends("risk_insurance_end_date")
    def _compute_risk_insurance_expired(self):
        today = fields.Date.context_today(self)
        for partner in self:
            partner.risk_insurance_expired = bool(
                partner.risk_insurance_end_date
                and partner.risk_insurance_end_date <= today
            )

    @api.model
    def _search_risk_insurance_expired(self, operator, value):
        today = fields.Date.context_today(self)
        if (operator == "=" and value) or (operator == "!=" and not value):
            return [
                ("risk_insurance_end_date", "!=", False),
                ("risk_insurance_end_date", "<=", today),
            ]
        return [
            "|",
            ("risk_insurance_end_date", "=", False),
            ("risk_insurance_end_date", ">", today),
        ]

    @api.depends("risk_remaining_percentage")
    def _compute_risk_coverage_display(self):
        for partner in self:
            coverage = 100.0 - (partner.risk_remaining_percentage or 0.0)
            partner.risk_coverage_display = f"{coverage:.2f}%"

    @api.depends(
        "risk_sale_order_include",
        "risk_invoice_draft_include",
        "risk_invoice_open_include",
        "risk_invoice_unpaid_include",
        "risk_account_amount_include",
        "risk_account_amount_unpaid_include",
        "risk_payment_return_include",
    )
    def _compute_risk_remaining_value_include(self):
        for partner in self:
            partner.risk_remaining_value_include = any(
                [
                    partner.risk_sale_order_include,
                    partner.risk_invoice_draft_include,
                    partner.risk_invoice_open_include,
                    partner.risk_invoice_unpaid_include,
                    partner.risk_account_amount_include,
                    partner.risk_account_amount_unpaid_include,
                    partner.risk_payment_return_include,
                ]
            )

    @staticmethod
    def _risk_match(total, operator, value):
        total = total or 0.0
        if operator == ">":
            return total > value
        if operator == ">=":
            return total >= value
        if operator == "<":
            return total < value
        if operator == "<=":
            return total <= value
        if operator == "=":
            return total == value
        if operator == "!=":
            return total != value
        return False

    @api.model
    def _risk_partner_ids_from_move_lines(self, domain, operator, value):
        """Return domain filtering partners with account.move.line amounts
        matching operator/value."""
        groups = self.env["account.move.line"].sudo()._read_group(
            domain=domain,
            groupby=["partner_id"],
            aggregates=["amount_residual:sum"],
        )
        partner_ids = [
            partner.id
            for partner, total in groups
            if self._risk_match(total, operator, value)
        ]
        return [("commercial_partner_id", "in", partner_ids)]

    @api.model
    def _search_risk_sale_order(self, operator, value):
        risk_states = self.env["sale.order"]._get_risk_states()
        groups = self.env["sale.order.line"].sudo()._read_group(
            domain=[("state", "in", risk_states)],
            groupby=["risk_partner_id"],
            aggregates=["risk_amount:sum"],
        )
        partner_ids = [
            p.id
            for p, total in groups
            if self._risk_match(total, operator, value)
        ]
        return [("commercial_partner_id", "in", partner_ids)]

    @api.model
    def _search_risk_invoice_draft(self, operator, value):
        domain = self._risk_account_groups()["draft"]["domain"]
        return self._risk_partner_ids_from_move_lines(domain, operator, value)

    @api.model
    def _search_risk_invoice_open(self, operator, value):
        domain = self._risk_account_groups()["open"]["domain"]
        return self._risk_partner_ids_from_move_lines(domain, operator, value)

    @api.model
    def _search_risk_invoice_unpaid(self, operator, value):
        domain = self._risk_account_groups()["unpaid"]["domain"]
        return self._risk_partner_ids_from_move_lines(domain, operator, value)

    @api.model
    def _search_risk_account_amount(self, operator, value):
        # Same domain as open but excludes lines on the partner's default
        # receivable account; use the open domain as a conservative approximation.
        domain = self._risk_account_groups()["open"]["domain"]
        return self._risk_partner_ids_from_move_lines(domain, operator, value)

    @api.model
    def _search_risk_account_amount_unpaid(self, operator, value):
        domain = self._risk_account_groups()["unpaid"]["domain"]
        return self._risk_partner_ids_from_move_lines(domain, operator, value)

    @api.model
    def _search_risk_payment_return(self, operator, value):
        company_domain = self._get_risk_company_domain()
        domain = company_domain + [
            ("reconciled", "=", False),
            ("account_type", "=", "asset_receivable"),
            ("partial_reconcile_returned_ids", "!=", False),
        ]
        return self._risk_partner_ids_from_move_lines(domain, operator, value)

    @api.model
    def _search_risk_amount_exceeded(self, operator, value):
        # risk_amount_exceeded > 0 is equivalent to risk_exception = True
        if operator in (">", ">=") and value >= 0:
            return self._search_risk_exception("=", True)
        return [("id", "=", False)]

    @api.model
    def _cron_reset_expired_insurance_credit_limit(self):
        """Reset insurance_credit_limit to 0 for partners whose insurance
        contract end date has been reached. Also restores credit_limit to the
        company-only portion so the company does not absorb the insured risk.
        Runs every 12 hours."""
        today = fields.Date.context_today(self)
        partners = self.search(
            [
                ("risk_insurance_end_date", "<=", today),
                ("insurance_credit_limit", "!=", 0),
            ]
        )
        for partner in partners:
            old_insurance_limit = partner.insurance_credit_limit
            currency = partner.risk_currency_id.name or ""
            partner.sudo().write({"insurance_credit_limit": 0.0})
            partner.sudo().write({"use_partner_credit_limit": False})
            partner.message_post(
                body=_(
                    "Insurance credit limit automatically reset to 0 "
                    "(was %(old_insurance)s %(currency)s). Credit limit restored "
                    "to company default because the insurance contract end date "
                    "%(end_date)s has been reached.",
                    old_insurance=old_insurance_limit,
                    currency=currency,
                    end_date=partner.risk_insurance_end_date,
                ),
                subtype_xmlid="mail.mt_note",
            )
