# -*- coding: utf-8 -*-
{
    'name': 'Sale Product Matrix Configurator',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Choose configuration mode before selecting products in sale orders',
    'description': """
Sale Product Matrix Configurator
================================

This module allows users to choose the configuration mode (Matrix Grid or Product Configurator) 
before selecting products in sale order lines, providing better control over the configuration workflow.

Key Features:
* Configuration mode selector appears before product selection
* Respects user choice and doesn't auto-open unwanted configurators
* Compatible with existing sale_product_matrix functionality
* Works with both matrix and configurator products
* Preserves custom attribute values for text-type attributes

The configuration mode field appears before the product selection, allowing users to choose
their preferred configuration method before selecting any product.
    """,
    'author': 'Antonio Canovas Pedreno',
    'website': 'https://github.com/antoniocanovas',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'sale_product_matrix',
        'product',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_product_matrix_configurator/static/src/js/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
