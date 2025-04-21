# © 2023 Serincloud ( https://www.puntsistemes.es )
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'FSC',
    'version': '18.0.1.0.0',
    'category': 'mrp',
    "license": "AGPL-3",
    'website': "https://puntsistemes.es",
    'summary': 'FSC Traceability',
    'author': 'Punt Sistemes',
    'depends': [
        'stock',
        'mrp',
        'product_material',
    ],
    'data': [
        'views/product_material_views.xml',
        'views/mrp_production_views.xml',
        'views/stock_lot_views.xml',
        'views/product_views.xml',
    ],
    'installable': True,
    'application': False,
}
