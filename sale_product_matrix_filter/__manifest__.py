# -*- coding: utf-8 -*-
{
    'name': 'Sale Product Matrix Filter',
    'version': '18.0.1.0.1',
    'category': 'Sales',
    'license': 'LGPL-3',
    'summary': 'Filter product matrix by attribute value in sale orders',
    'description': """
Sale Product Matrix Filter
==========================

This module extends the sale product matrix functionality to allow
filtering the matrix display based on multiple attribute values.

Key Features:
* Add value_filter_ids field to sale orders (Many2many)
* Filter matrix products to show variants with any of the selected attributes
* Support for multiple attribute value filtering simultaneously
* **Auto-assignment of filters based on partner configuration**
* **Fallback to company default filter values**
* **Smart filter inheritance: Partner → Company defaults**
* Maintains existing matrix functionality
* User-friendly interface with tags widget

Perfect for scenarios where you want to focus on specific product variants
during the sales process, such as filtering by size, color, or any other
product attribute.

Version History:
* v18.0.1.0.0: Complete implementation with smart filter inheritance (Partner → Company defaults)
    """,
    'author': 'Antonio Canovas Pedreno',
    'website': 'https://www.antoniocanouvas.com',
    'depends': [
        'product',
        'stock',
        'sale',
        'sale_product_matrix',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/res_company_views.xml',
        'views/res_partner_views.xml',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_product_matrix_filter/static/src/js/product_matrix_dialog_patch.js',
        ],
    },
    'demo': [],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'external_dependencies': {},
}
