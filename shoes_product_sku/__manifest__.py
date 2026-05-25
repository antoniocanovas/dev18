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
    "name": "Shoes Product SKU",
    "version": "18.0",
    "depends": [
        "base",
        "product",
        "shoes_dealer",
        "shoes_campaign",
        "shoes_color_chart",
    ],
    "author": "Punt Sistemes",
    "category": "Project",
    "website": "https://www.puntsistemes.es",
    "description": """
        Shoes product auto SKU. 
    """,
    "data": [
        "security/ir.model.access.csv",
        "security/shoes_stock_referrer_rules.xml",
        "data/shoes_product_sku_item.xml",
        "data/shoes_sku_sequence.xml",
        "data/shoes_stock_referrer_sequence.xml",
        "views/shoes_sku_views.xml",
        "views/shoes_stock_referrer_views.xml",
        "views/shoes_sku_image_import_views.xml",
        "views/res_partner_views.xml",
        "views/res_company_views.xml",
        "views/project_task_views.xml",
        "views/project_project_views.xml",
        "views/product_template_views.xml",
        "data/server_actions.xml",
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
