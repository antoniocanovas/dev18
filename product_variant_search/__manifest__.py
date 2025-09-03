{
    'name': 'Product Variant Search',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Búsqueda flexible de variantes de producto en líneas de venta',
    'description': """
        Este módulo permite buscar productos en las líneas de venta por el nombre 
        de la plantilla o cualquier variante, independientemente del orden de las palabras.
        
        Características:
        - Búsqueda por nombre de producto y valores de atributo
        - Orden independiente de las palabras de búsqueda
        - Optimizado con campo calculado y almacenado
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'product',
        'sale',
    ],
    'data': [
        'data/product_data.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
