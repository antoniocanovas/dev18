##############################################################################
#
#    Punt Sistemes SL
#    Copyright (C) 2024 - Punt Sistemes (http://www.puntsistemes.es). All Rights Reserved  # noqa: E501
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
    "name": "Shoes Pricelist",
    "version": "18.0",
    "depends": ["sale_management", "shoes_dealer", "intrastat_duty"],
    "author": "Punt Sistemes",
    "category": "Sales",
    "website": "https://www.puntsistemes.es",
    "description": """
        Shoes dealer pricelist. 
    """,
    "data": [
        "security/ir.model.access.csv",
        "views/shoes_pricelist_views.xml",
        "views/product_pricelist_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
