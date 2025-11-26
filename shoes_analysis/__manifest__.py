{
    "name": "Shoes Analysis",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Informes específicos para distribución de calzado",
    "description": """
        Módulo de análisis e informes para el sector de distribución de calzado.
        Proporciona informes personalizados basados en campañas, lotes y distribuidores.
    """,
    "author": "Tu Empresa",
    "website": "https://www.tuempresa.com",
    "license": "LGPL-3",
    "depends": [
        "sale",
        "stock",
        "account",
        "shoes_dealer",
        "shoes_campaign",
        "purchase_lot_preassignment",
        "sale_order_type",
    ],
    "data": [
        "report/sale_report_views.xml",
        "report/account_invoice_report_views.xml",
        "security/ir.model.access.csv",
        "views/shoes_analysis_views.xml",
        "views/shoes_analysis_menu.xml",
        "views/product_template_views.xml",
        "report/shoes_analysis_report.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False,
}
