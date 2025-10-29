# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from typing import Any

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shoes_task_id = fields.Many2one(
        "project.task", string="Shoes model", ondelete="restrict"
    )
    shoes_last_id = fields.Many2one("shoes.last", string="Last", ondelete="restrict")
    shoes_model_material_id = fields.Many2one(
        "shoes.model.material", string="Model code"
    )

    def _get_pair_and_variants_sync(self):
        super()._get_pair_and_variants_sync()
        if self.intrastat_duty_id:
            country = (self.intrastat_duty_id.country_id,)
            intrastat = (self.intrastat_duty_id.intrastat_id,)

            self.product_tmpl_single_id.write(
                {
                    "intrastat_duty_id": self.intrastat_duty_id.id,
                    "hs_code": self.hs_code,
                    "country_of_origin": country,
                    "image_1920": self.image_1920,
                }
            )

            if self.shoes_pair_weight_id.id:
                for assortment in self.product_variant_ids:
                    assortment.write(
                        {
                            "intrastat_code_id": intrastat,
                            "intrastat_origin_country_id": country,
                        }
                    )

                for pair in self.product_tmpl_single_id.product_variant_ids:
                    pair.write(
                        {
                            "intrastat_code_id": intrastat,
                            "intrastat_origin_country_id": country,
                        }
                    )

    def create_shoe_pairs(self) -> Any:
        # 1) Ejecutamos el comportamiento original: creación de pares
        res = super().create_shoe_pairs()
        # 2) Tras crear las plantillas “single”, propagamos shoes_last_id
        # y shoes_model_material
        for record in self:
            shoes_model_material = self.env["shoes.model.material"].search(
                [
                    ("task_id", "=", record.shoes_task_id.id),
                    ("material_id", "=", record.material_id.id),
                ]
            )
            if record.shoes_last_id and record.product_tmpl_single_id:
                record.product_tmpl_single_id.write(
                    {
                        "shoes_last_id": record.shoes_last_id.id,
                    }
                )
            if shoes_model_material.id:
                record.write({"shoes_model_material_id": shoes_model_material.id})
                record.product_tmpl_single_id.write(
                    {"shoes_model_material_id": shoes_model_material.id}
                )
        # 3) Devolvemos lo que devolvía el super (si lo hubiera)
        return res
