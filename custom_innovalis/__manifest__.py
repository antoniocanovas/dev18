# -*- coding: utf-8 -*-
{
    'name': "Custom Innovalis",
    'summary': """Campos personalizados para res.partner Innovalis""",
    'description': """
        Añade campos personalizados específicos de Innovalis al modelo res.partner
        organizados en una nueva pestaña "Innovalis".
    """,
    'author': "Punt Sistemes",
    'version': '18.0.1.0.0',
    'depends': ['base', 'contacts'],
    'data': [
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
