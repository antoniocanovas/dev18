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
    "name": "Shoes eCommerce",
    "version": "18.0",
    "depends": [
        "shoes_product_sku",
        "website_sale",
    ],
    "author": "Punt Sistemes",
    "category": "Project",
    "website": "https://www.puntsistemes.es",
    "description": """
        eCommerce integration for Shoes Product SKU.
        - Main carousel image uses shoes.sku image when the variant has a SKU assigned.
        - Carousel appends shoes.sku product_image_ids after the standard images.
    """,
    "data": [],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
