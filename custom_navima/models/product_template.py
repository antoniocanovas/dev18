# Copyright 2024 Punt Sistemes SL

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    display_name = fields.Char(
        string="Display Name", compute="_compute_display_name", store=False
    )

    @api.depends("name", "is_pair", "is_assortment", "shoes_model_material")
    def _compute_display_name(self):
        for record in self:
            name = record.name or ""

            # Si es un producto tipo par o assortment Y tiene shoes_model_material_id
            if (
                record.is_pair or record.is_assortment
            ) and record.shoes_model_material:
                name = f" [{record.shoes_model_material}] "
                name += record.name

            record.display_name = name
