# -*- coding: utf-8 -*-
{
    'name': 'Sale Product Matrix Configurator',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Allow product configurator mode for matrix products in sale orders',
    'description': """
        This module extends sale_product_matrix to allow switching between
        matrix grid and product configurator modes on sale order lines,
        even for products configured with matrix mode.
        
        Features:
        - Add configurator_mode field on sale order lines
        - Allow switching between matrix and configurator modes
        - Open product configurator dialog for matrix products
        - Maintain existing functionality
    """,
    'author': 'Antonio Canovas Pedreno',
    'website': '',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'sale_product_matrix',
        'product_matrix',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_product_matrix_configurator/static/src/js/**/*',
            'sale_product_matrix_configurator/static/src/xml/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
