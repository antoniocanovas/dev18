{
    "name": "Shoes Product Pricelist Retail",
    "version": "18.0.1.0.0",
    "category": "Sales",
    "summary": "Add retail pricelist reference and RRP/PVP on sales orders, per pair",
    "description": """
Shoes Product Pricelist Retail
========================
Adds retail price (RRP/PVP) functionality to sales orders, per pair:
- Retail pricelist reference field on pricelists
- Automatic RRP/PVP calculation on sale order lines
- RRP/PVP column in quotation/order PDF reports
- Based on product_pricelist_retail change the price of assortments to pair.
    """,
    "author": "Antonio Canovas",
    "depends": ["sale_management", "product", "product_pricelist_retail"],
    "data": [
        "views/product_pricelist_views.xml",
        "views/sale_order_views.xml",
        "views/report_saleorder.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
