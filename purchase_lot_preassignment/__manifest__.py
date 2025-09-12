{
    "name": "Purchase Lot Preassignment",
    "version": "18.0.0.1",
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
    ),
    "author": "Punt Sistemes",
    "depends": ["purchase", "stock", "purchase_stock", "web", "product"],
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_order_views.xml",
        "views/purchase_lot_preassignment_views.xml",
        "views/stock_picking_views.xml",
        "wizard/purchase_lot_preassignment_label_layout_views.xml",
        "report/purchase_lot_preassignment_report_views.xml",
        "report/report_purchase_lot_preassignment_label.xml",
        "report/purchase_lot_preassignment_templates.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
