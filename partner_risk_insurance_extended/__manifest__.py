# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Partner Risk Insurance Extended",
    "version": "18.0.1.0.1",
    "development_status": "Beta",
    "summary": (
        "Establece valores de riesgo por defecto a True y añade vista "
        "de seguimiento Partner Risk en Contabilidad"
    ),
    "author": "AvanzOSC",
    "license": "AGPL-3",
    "application": False,
    "website": "https://github.com/OCA/credit-control",
    "depends": [
        "account_financial_risk",
        "partner_risk_insurance",
        "account_payment_return_financial_risk",
        "sale_financial_risk",
    ],
    "category": "Credit Control",
    "data": [
        "data/automated_actions.xml",
        "views/res_partner_risk_view.xml",
    ],
    "installable": True,
    "post_init_hook": "post_init_hook",
}
