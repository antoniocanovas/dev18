# -*- coding: utf-8 -*-
{
    'name': 'Purchase Product Matrix Configurator',
    'version': '1.0',
    'category': 'Purchase',
    'summary': 'Configuration preferences and variable values for purchase orders',
    'description': """
Purchase Product Matrix Configurator
====================================

This module allows users to set configuration preferences and manage variable values 
for products in purchase order lines. It provides consistency with sale orders while 
respecting purchase-specific limitations.

Key Features:
* Configuration mode field for consistency with sales
* Variable value fields for additional costs/adjustments
* Automatic calculation of totals including variables
* Compatible with existing purchase_product_matrix functionality
* Always uses Matrix Grid (the only option available in purchase)
* Visual feedback about configuration preferences

Variable Fields Added:
* variable_value: Variable value per line
* variable_percentage: Variable percentage applied
* variable_cost: Variable cost per unit
* price_total_with_variable: Computed total including variables

The configuration mode field appears before product selection for consistency,
and variable fields allow flexible cost adjustments per purchase line.
    """,
    'author': 'Antonio Canovas Pedreno',
    'website': 'https://github.com/antoniocanovas',
    'license': 'LGPL-3',
    'depends': [
        'purchase',
        'purchase_product_matrix',
        'product',
    ],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'purchase_product_matrix_configurator/static/src/js/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
