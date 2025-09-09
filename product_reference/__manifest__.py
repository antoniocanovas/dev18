# -*- coding: utf-8 -*-
{
    'name': 'Product Reference',
    'version': '18.0.1.0.0',
    'category': 'Product',
    'summary': 'Gestión de referencias de productos con compatibilidades simétricas',
    'description': """
Product Reference Management
============================

Este módulo permite gestionar referencias de productos con sistema de compatibilidades simétricas.

Características principales:
* Crear referencias de productos
* Definir compatibilidades entre referencias
* Sistema simétrico automático (si A es compatible con B, entonces B es compatible con A)
* Wizard para gestión fácil de compatibilidades
* Tabla de relación optimizada

    """,
    'author': 'Tu Nombre',
    'website': 'https://www.tuempresa.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/product_reference_views.xml',
        'views/product_reference_compatibility_wizard_views.xml',
    ],
    'demo': [
        'data/product_reference_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
