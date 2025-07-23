# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Purchase Line Link MTO Enhancement',
    'version': '18.0.1.0.0',
    'category': 'Sales/Purchase',
    'summary': 'Backend linking of sale lines to purchase lines in MTO (no UI views)',
    'description': """
Sale Purchase Line Link MTO Enhancement - Backend Only
======================================================

Este módulo proporciona funcionalidad BACKEND para vincular
líneas de venta con líneas de compra en procesos Make-to-Order (MTO).

Funcionalidades Backend:
-----------------------
* Propaga sale_line_id desde stock.move a procurement values
* Mantiene la vinculación a través de stock rules  
* Campo customer_id calculado automáticamente
* Compatible con rutas MTO + Buy
* Sin vistas XML - solo funcionalidad programtica

Campos Disponibles Programticamente:
-----------------------------------
* purchase.order.line.sale_line_id: Vincula a sale.order.line original
* purchase.order.line.customer_id: Cliente final (calculado desde sale_line_id)

Uso:
----
# Acceder a la vinculación desde código:
po_line = env['purchase.order.line'].browse(123)
if po_line.sale_line_id:
    sale_order = po_line.sale_line_id.order_id
    customer = po_line.customer_id
    print(f"PO generada desde SO: {sale_order.name} para {customer.name}")

Casos de uso:
------------
* Reportes personalizados con trazabilidad completa
* Análisis de márgenes SO vs PO por cliente
* Automatizaciones que requieren vinculación SO-PO
* Integraciones y APIs con datos vinculados
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': [
        'sale_stock',
        'purchase_stock',
        'sale_purchase_stock',
    ],
    'data': [
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
