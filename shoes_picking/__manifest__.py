# Copyright Serincloud SL - 2025
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "Shoes Picking - Aprobación Comercial",
    "summary": "Validación comercial previa al despacho de albaranes de salida.",
    "version": "18.0.1.0.0",
    "category": "stock",
    "author": "Serincloud SL",
    "website": "https://www.ingenieriacloud.com",
    "license": "AGPL-3",
    "depends": ["sale_stock"],
    "data": [
        "security/shoes_picking_security.xml",
        "data/server_actions.xml",
        "views/stock_picking_views.xml",
    ],
    "installable": True,
    "auto_install": False,
}
