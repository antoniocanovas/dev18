from typing import Any

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    public_ean_sequence = fields.Boolean(
        string="'Public EAN sequence'",
        config_parameter="pnt_product_ean_barcode.public_ean_sequence",
        help="Si está marcado, el menú 'EAN sequence' sera visible.",
        default=True,
    )
    internal_ean_sequence = fields.Boolean(
        string="'Internal EAN sequence'",
        config_parameter="pnt_product_ean_barcode.internal_ean_sequence",
        help="Si está marcado, el menú 'Internal EAN sequence' sera visible.",
        default=True,
    )

    @api.model
    def get_values(self) -> Any:
        res = super().get_values()
        params = self.env["ir.config_parameter"].sudo()
        res.update(
            {
                "public_ean_sequence": params.get_param(
                    "pnt_product_ean_barcode.public_ean_sequence", default="False"
                )
                == "True",
                "internal_ean_sequence": params.get_param(
                    "pnt_product_ean_barcode.internal_ean_sequence", default="False"
                )
                == "True",
            }
        )
        return res

    def set_values(self):
        super().set_values()
        params = self.env["ir.config_parameter"].sudo()
        # Guarda los parámetros explícitamente
        params.set_param(
            "pnt_product_ean_barcode.public_ean_sequence", str(self.public_ean_sequence)
        )
        params.set_param(
            "pnt_product_ean_barcode.internal_ean_sequence",
            str(self.internal_ean_sequence),
        )
        # Activa/desactiva menús según el valor guardado
        menu_internal = self.env.ref(
            "pnt_product_ean_barcode.pnt_menu_internal_ean_sequence",
            raise_if_not_found=False,
        )
        menu_public = self.env.ref(
            "pnt_product_ean_barcode.pnt_menu_ean_sequence", raise_if_not_found=False
        )
        if menu_internal:
            menu_internal.active = self.internal_ean_sequence
        if menu_public:
            menu_public.active = self.public_ean_sequence
