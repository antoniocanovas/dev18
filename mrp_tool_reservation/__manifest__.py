# © 2023 Serincloud ( https://www.puntsistemes.es )
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'MRP Tools',
    'version': '18.0.1.0.0',
    'category': 'mrp',
    "license": "AGPL-3",
    'website': "https://puntsistemes.es",
    'summary': 'MRP Tools reservation',
    'author': 'Punt Sistemes',
    'depends': [
        'mrp',
        'maintenance',
    ],
    'data': [
        'views/mrp_production_views.xml',
        'views/mrp_bom_views.xml',
        'views/res_company_views.xml',
    ],
    'installable': True,
    'application': False,
}
