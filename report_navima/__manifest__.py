##############################################################################
#
#    Punt Sistemes SL
#    Copyright (C) 2024 - Punt Sistemes (http://www.puntsistemes.es). All Rights
#    Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

{
    "name": "reports navima",
    "version": "18.0",
    "depends": [
        "purchase",
        "sale_product_matrix",
        "sale_product_image",
        "pnt_mass_ir_action_report",
        "shoes_analysis",
    ],
    "author": "Punt Sistemes",
    "category": "Project",
    "website": "https://www.puntsistemes.es",
    "description": """
        añade tabla de datos en la vista presupuesto,compras y ventas
    """,
    "data": [
        "security/ir.model.access.csv",
        "views/purchase_line_shoes_pair_line_views.xml",
        "views/purchase_order_line_views.xml",
        "views/purchase_order_views.xml",
        "reports/sale_order.xml",
        "reports/account_invoice_report_templates.xml",
        "reports/purchase_order.xml",
        "reports/report_delivery.xml",
        "reports/lot_label_reports.xml",
        "reports/lot_label_templates.xml",
        "reports/location_barcode_templates.xml",
        "reports/purchase_shoes_size_matrix_report.xml",
        "reports/packing_list_report.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
