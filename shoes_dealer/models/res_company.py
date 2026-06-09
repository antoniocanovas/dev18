# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    is_shoes_company = fields.Boolean("Shoes company", default=True)
    assortment_attribute_id = fields.Many2one(
        "product.attribute", string="Assortment attribute", store=True
    )
    size_attribute_id = fields.Many2one(
        "product.attribute", string="Size attribute", store=True
    )
    color_attribute_id = fields.Many2one(
        "product.attribute", string="Color attribute", store=True
    )
    assortment_prefix = fields.Char("Assortment prefix", store=True)
    single_prefix = fields.Char("Single prefix", store=True)
    single_sale = fields.Boolean("Enable pair sales", store=True, default=False)
    single_purchase = fields.Boolean("Enable pair purchase", store=True, default=False)
    shoes_assortment_custom_label = fields.Char(
        "Custom assortment label",
        store=True,
        help=(
            "Etiqueta que aparece en la sección 'Pack' de la etiqueta de lote cuando el surtido "
            "es de tipo personalizado (custom=True), es decir, creado automáticamente desde el "
            "wizard de cuadrícula de líneas de venta.\n\n"
            "Si está vacío se muestra 'ESPECIAL'.\n\n"
            "AVISO: este valor solo afecta a la impresión. Los registros shoes.assortment siguen "
            "usando el código de composición como nombre (ej: '35x2+36x4+37x2'), lo que garantiza "
            "su unicidad. Sin embargo, el valor de atributo de producto vinculado a cada surtido "
            "custom también se nombra con ese código, por lo que en los desplegables del producto "
            "seguirán apareciendo los códigos técnicos, no esta etiqueta."
        ),
    )
    exwork_currency_id = fields.Many2one(
        "res.currency",
        store=True,
        default=lambda self: self.env.user.company_id.currency_id,
    )
    shoes_pair_weight_std = fields.Boolean("Pair standard price", default=True)
    shoes_hs_code_std = fields.Boolean("Standard HS code", default=True)
    shoes_pair_uom_id = fields.Many2one(
        "uom.uom",
        string="Pair UOM",
        default=lambda self: self.env.ref(
            "shoes_dealer.shoes_pair_uom", raise_if_not_found=False
        ),
    )
    shoes_assortment_uom_id = fields.Many2one(
        "uom.uom",
        string="Assortment UOM",
        default=lambda self: self.env.ref(
            "shoes_dealer.shoes_assortment_uom", raise_if_not_found=False
        ),
    )

    # Shoes tracking:
    shoes_assortment_tracking = fields.Selection(
        [("lot", "Lot"), ("serial", "Serial Number"), ("none", "None")],
        string="Assortment tracking",
        default="lot",
    )
    shoes_pair_tracking = fields.Selection(
        [("lot", "Lot"), ("serial", "Serial Number"), ("none", "None")],
        string="Pair tracking",
        default="none",
    )

    # Auto SYNC options:
    shoes_categ_sync = fields.Boolean(
        "AutoSYNC Category",
        help="Pair and assortment sync accounting category when enabled.",
        default=True,
    )

    # Lot name composition:
    lot_name_campaign = fields.Boolean(
        "Campaign",
        default=False,
        help="Prefija el nombre del lote con el nombre de la campaña del pedido.",
    )
    lot_name_manufacturer = fields.Boolean(
        "Manufacturer",
        default=False,
        help="Prefija el nombre del lote con el campo ref del fabricante del producto.",
    )
    lot_name_brand = fields.Boolean(
        "Brand",
        default=False,
        help="Prefija el nombre del lote con el código de la marca del producto.",
    )
    lot_name_sequence = fields.Many2one(
        "ir.sequence",
        string="Lot sequence",
        default=lambda self: self.env.ref(
            "stock.sequence_production_lots", raise_if_not_found=False
        ),
        help="Secuencia utilizada para generar el nombre del lote (sufijo tras el prefijo). "
             "Por defecto usa la secuencia estándar de Odoo para lotes/series.",
    )
