# -*- coding: utf-8 -*-
{
    'name': 'Sale Variant Toggle',
    'version': '18.0.1.1.0',
    'category': 'Sales',
    'summary': 'Permite alternar entre formato matriz y configurador para variantes de producto',
    'description': """
    Sale Variant Toggle - Funcional para Odoo 18
    =============================================
    
    Este módulo permite alternar dinámicamente entre el formato de configurador 
    de productos y el formato de matriz/cuadrícula en las líneas de venta.
    
    Características:
    * Campo "Variant Selection Mode" en product.template
    * Opción "Allow Toggle" que intercepta la selección de productos
    * Diálogo JavaScript que permite elegir formato al vuelo
    * Integración con configuradores nativos de Odoo
    * Compatible con Odoo 18 (sin attrs/states)
    
    Uso:
    1. Configura un producto con variantes como "Allow Toggle"
    2. Al agregar el producto a líneas de venta, aparece el diálogo
    3. Elige entre Configurador o Matriz según tus necesidades
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'sale',
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
        'views/sale_order_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sale_variant_toggle/static/src/js/variant_configurator.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
}
