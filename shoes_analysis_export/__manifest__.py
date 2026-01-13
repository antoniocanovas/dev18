{
    'name': 'Exportación de Análisis de Calzado',
    'version': '1.0',
    'summary': 'Proporciona la estructura de datos para exportar informes de análisis de calzado.',
    'author': 'Your Name',
    'category': 'Inventory/Product',
    'depends': [
        'shoes_analysis',
        'product',
        'project',
        'sale_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/shoes_analysis_main_extend_views.xml',
        'views/shoes_analysis_export_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
