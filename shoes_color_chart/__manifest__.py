# -*- coding: utf-8 -*-
##############################################################################
#
#    Punt Sistemes SL
#    Copyright (C) 2024 - Punt Sistemes (http://www.puntsistemes.es). All Rights Reserved
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
    "name": 'Shoes Color Chart',
    "version": '18.0',
    "depends": [
        'product',
        'project',
        'partner_product_attribute_value',
        'shoes_dealer',
        'shoes_campaign',
    ],
    "author": "Punt Sistemes",
    "category": 'Project',
    "website": "https://www.puntsistemes.es",
    "description": """
        Shoes color chart by campaign. 
    """,
    "data": [
        "security/ir.model.access.csv",
        'views/shoes_color_chart_wizard_views.xml',
        'views/shoes_color_chart_copy_wizard_views.xml',
        'views/shoes_color_chart_item_views.xml',
        'views/project_project_views.xml',
        'views/project_task_views.xml',
        'views/product_template_views.xml',
        'views/product_attribute_views.xml',
        'views/product_material_views.xml',
    ],
    "demo": [],
    "installable": True,
    "auto_install": False,
}
