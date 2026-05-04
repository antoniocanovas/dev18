{
    "name": "Shoes Purchase",
    "version": "18.0.1.0.0",
    "category": "Purchase",
    "summary": "Wizard para dividir y fusionar pedidos de compra",
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
        "data/purchase_merge_server_action.xml",
        "wizard/purchase_split_wizard_views.xml",
        "wizard/purchase_merge_wizard_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
