# Copyright Punstsistemes SL - Puntsistemes.es


from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = ["product.category"]

    pnt_ean_required = fields.Boolean(
        string="EAN required",
        help=(
            "When enabled, products in this category are expected to carry an EAN "
            "barcode. A warning will be displayed on any product that has no barcode "
            "assigned, and the default EAN sequence defined below will be pre-selected "
            "automatically when opening the barcode assignment wizard."
        ),
    )
    pnt_default_ean_sequence_id = fields.Many2one(
        "ir.sequence",
        string="Default EAN Sequence",
        domain=[("pnt_is_ean", "=", True)],
        help="Default EAN sequence for products in this category",
    )
