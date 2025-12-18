{
    'name': 'Gift Registry Extension',
    'version': '1.0',
    'summary': 'Extends sales and PoS for gift registry functionality.',
    'description': """
        This module provides a complete gift registry solution for Odoo 19 Enterprise.
        - Extends Sale Orders to act as Gift Registries.
        - Integrates with Point of Sale (PoS) for loading and managing registries.
        - Allows purchasing against a gift registry from both Sales and PoS.
        - Provides a customer portal view for their gift registries.
    """,
    'author': 'Your Name',
    'website': 'https://www.yourcompany.com',
    'category': 'Sales/Sales',
    'depends': ['sale', 'point_of_sale', 'website', 'website_sale'],
    'data': [
        'views/sale_order_views.xml',
        'views/portal_templates.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'gift_registry_extension/static/src/js/gift_registry_buttons.js',
            'gift_registry_extension/static/src/xml/gift_registry_pos.xml',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
}
