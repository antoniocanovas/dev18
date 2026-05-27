# Copyright Puntsistemes - 2024
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "PNT Product EAN Barcode",
    "summary": "Generation of EAN codes based on customer prefix",
    "version": "18.0.1.0.1",
    "category": "stock",
    "author": "Pedro Guirao Puntsistemes, Adrian Muñoz Puntsistemes",
    "website": "https://www.puntsistemes.es",
    "license": "AGPL-3",
    "depends": [
        "stock",
        "product",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/pnt_ir_sequence_view.xml",
        "views/pnt_menu.xml",
        "views/pnt_product_category_view.xml",
        "views/pnt_product_product_view.xml",
        "views/pnt_product_template_view.xml",
        "views/res_config_settings_views.xml",
        "views/pnt_assign_ean_wizard_view.xml",
    ],
    "external_dependencies": {
        "python": [
            "gtin",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
