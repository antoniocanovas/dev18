# -*- coding: utf-8 -*-
{
    'name': 'Shoes Analysis Export',
    'version': '18.0.1.0.0',
    'category': 'Sales',
    'summary': 'Funcionalidad de exportación para los informes de Shoes Analysis',
    'description': """
        Este módulo añade la funcionalidad de exportación a hojas de cálculo de Odoo
        para los informes generados por el módulo Shoes Analysis.
    """,
    'author': 'Tu Empresa',
    'website': 'https://www.tuempresa.com',
    'license': 'LGPL-3',
    'depends': [
        'shoes_analysis', # Dependency on the main module
        'spreadsheet_dashboard', # For Odoo Spreadsheet integration
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/shoes_analysis_export_views.xml',
        'views/shoes_analysis_main_extend_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
