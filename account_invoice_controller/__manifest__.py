{
    'name': 'Account Invoice Controller',
    'version': '1.0',
    'summary': 'Webhook para crear facturas de cliente via JSON API',
    'author': 'Tu Nombre',
    'depends': ['base', 'account', 'product', 'custom_innovalis'],
    'application': False,
    'installable': True,
    'data': [
        'security/ir.model.access.csv',
        'views/webhook_token_views.xml',
    ],
    'license': 'LGPL-3',
}
