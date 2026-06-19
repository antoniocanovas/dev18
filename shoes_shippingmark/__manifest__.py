##############################################################################
#
#    Punt Sistemes SL
#    Copyright (C) 2024 - Punt Sistemes (http://www.puntsistemes.es).
#    All Rights Reserved
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
    "name": "Shoes Shipping Mark",
    "version": "18.0.1.0.0",
    "depends": [
        "sale_order_type",
        "sale_stock",
        "account",
        "stock",
        "purchase",
    ],
    "author": "Punt Sistemes",
    "category": "Sales",
    "website": "https://www.puntsistemes.es",
    "description": """
        Gestión de Shipping Marks para clientes.
        Permite parametrizar exclusividad de shipping marks por cliente.
    """,
    "data": [
        "views/res_company_views.xml",
        "views/res_partner_views.xml",
        "views/sale_order_views.xml",
        "views/stock_lot_views.xml",
        "views/purchase_order_views.xml",
        "views/stock_picking_views.xml",
        "views/account_move_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
