{
    "name": "Purchase Lot Preassignment",
    "version": "18.0.0.2",
    "category": "Purchase",
    "summary": "Pre-assign lots/serial numbers in purchase orders before reception",
    "description": (
        "This module allows to create and pre-assign lots/serial numbers in purchase "
        "orders before receiving the products, so external manufacturers can assign "
        "the desired lots and validate them during reception."
        "Features:"
        "- Button in purchase orders to generate preassigned lots"
        "- Table of preassigned lots by product and purchase line"
        "- Validation during reception that expected lots match received ones"
        "- Support for both lots and serial numbers tracking"
        "- Integration with Barcode app (Enterprise) for preassigned lot handling"
    ),
    "author": "Punt Sistemes",
    "depends": [
        "purchase",
        "stock",
        "purchase_stock",
        "web",
        "product",
        "sale",
        "sale_purchase",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/automated_actions.xml",
        "report/purchase_lot_label_reports.xml",
        "report/purchase_lot_label_templates.xml",
        "report/purchase_lot_label_zpl.xml",
        "wizard/purchase_lot_view_wizard_views.xml",
        "wizard/sale_lot_view_wizard_views.xml",
        "views/res_company_views.xml",
        "views/purchase_order_views.xml",
        "views/sale_order_views.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
