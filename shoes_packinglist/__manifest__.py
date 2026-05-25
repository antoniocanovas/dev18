{
    "name": "Shoes Packing List",
    "summary": "Import container packing lists and match stock pickings.",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "Ingenieriacloud",
    "depends": [
        "purchase_container",
        "stock",
        "account",
        "product_net_weight",
        "product_dimension",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/packing_list_warning_wizard_views.xml",
        "wizard/container_validate_wizard_views.xml",
        "views/product_product_views.xml",
        "views/stock_lot_views.xml",
        "views/purchase_container_line_views.xml",
        "views/purchase_container_views.xml",
        "reports/packing_list_report.xml",
    ],
}
