{
    "name": "Shoes Purchase",
    "version": "18.0.1.0.0",
    "category": "Purchase",
    "summary": "Wizard para dividir pedidos de compra en dos",
    "author": "Punt Sistemes",
    "depends": [
        "purchase",
        "sale_purchase",
        "shoes_dealer",
        "purchase_lot_preassignment",
        "shoes_shippingmark",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/purchase_split_wizard_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
