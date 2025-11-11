# Copyright 2025 Serincloud SL - Ingenieriacloud.com
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Shoes Analysis",
    "summary": "Sales analysis for pairs and assortments",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "author": "Serincloud SL",
    "website": "https://www.ingenieriacloud.com",
    "license": "AGPL-3",
    "depends": [
        "shoes_dealer",
        "sale",
        "mrp",
        "account_reports",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/shoes_sales_statistics_report_data.xml",
        "views/shoes_dealer_analysis_views.xml",
        "views/shoes_sales_statistics_filters.xml",
        "views/menu_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "shoes_analysis_old/static/src/**/*.js",
        ],
    },
    "installable": False,
    "auto_install": False,
}
