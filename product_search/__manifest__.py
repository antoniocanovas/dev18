{
    'name': 'Búsqueda Inteligente de Productos',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Búsqueda de productos mediante texto libre con IA',
    'description': """
        Módulo que permite realizar búsquedas inteligentes de productos
        mediante texto libre y mostrar los resultados de forma dinámica.
        
        Características:
        - Búsqueda mediante texto libre
        - Detección automática de marcas y categorías
        - Sistema conversacional inteligente
        - Aprendizaje automático de patrones
        - Interfaz chat para mejorar búsquedas
        - Puntuación de relevancia
        - Analytics y reportes
        - Efectos visuales modernos
        - Tests automatizados
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'depends': ['base', 'product', 'sale', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/demo_data.xml',
        'views/product_search_views.xml',
        'views/product_search_interactive_views.xml',
        'views/product_search_menu.xml',
        'wizard/product_search_interaction_wizard.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'product_search/static/src/css/product_search.css',
            'product_search/static/src/js/product_search.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'price': 199.00,
    'currency': 'USD',
    'images': [
        'static/description/banner.png',
        'static/description/screenshot1.png',
        'static/description/screenshot2.png',
    ],
    'maintainers': ['tu-usuario-github'],
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
}