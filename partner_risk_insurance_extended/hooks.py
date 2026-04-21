# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging

logger = logging.getLogger(__name__)

RISK_INCLUDE_FIELDS = [
    "risk_sale_order_include",
    "risk_invoice_draft_include",
    "risk_invoice_open_include",
    "risk_invoice_unpaid_include",
    "risk_account_amount_include",
    "risk_account_amount_unpaid_include",
    "risk_payment_return_include",
]


def post_init_hook(env):
    """Set risk include fields to True for all existing partners."""
    logger.info(
        "Setting risk include fields to True for all existing res.partner records"
    )
    set_clauses = ", ".join(f"{field} = TRUE" for field in RISK_INCLUDE_FIELDS)
    env.cr.execute(f"UPDATE res_partner SET {set_clauses}")  # noqa: S608
