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
    "name": "Shoes intrastat duty estimation",
    "version": "18.0",
    "depends": [
        "product",
        "shoes_dealer",
        "intrastat_duty",
    ],
    "author": "Punt Sistemes",
    "category": "Stock",
    "website": "https://www.puntsistemes.es",
    "description": """
        Intrastat duty estimation for PAIR products.
        Field and views in product.template form.
    """,
    "data": [
        "views/product_template_views.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
