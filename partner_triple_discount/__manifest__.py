{
    "name": "Partner Triple Discount",
    "version": "18.0.1.0.0",
    "category": "Sales/Accounting",
    "author": "Punt Sistemes",
    "license": "AGPL-3",
    "summary": "Default triple discounts on partners, inherited in sales and invoices",
    "depends": ["sale_triple_discount", "account_invoice_triple_discount", "sale_product_matrix"],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_views.xml",
        "views/sale_order_discount_views.xml",
        "views/sale_order_views.xml",
        "wizard/account_move_triple_discount_views.xml",
        "views/account_move_views.xml",
    ],
    "installable": True,
}
