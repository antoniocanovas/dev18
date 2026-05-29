# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from typing import Any

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shoes_task_id = fields.Many2one(
        "project.task", string="Shoes model", ondelete="restrict"
    )
    trade_name = fields.Char(
        related="shoes_task_id.trade_name",
        store=True,
    )
    shoes_url = fields.Char(string="URL", related="shoes_task_id.shoes_url")
    shoes_last_id = fields.Many2one("shoes.last", string="Last", ondelete="restrict")
    shoes_model_material = fields.Char(
        related="shoes_task_id.shoes_model_material",
        string="Model code",
    )

    shoes_attribute_pending = fields.Boolean(
        "Producto pendiente de establecer atributos de surtido o color",
        store=True,
        compute="_compute_shoes_attribute_pending",
    )

    @api.depends("shoes_task_id", "is_pair", "is_assortment")
    def _compute_shoes_attribute_pending(self):
        for record in self:
            record.shoes_attribute_pending = (
                bool(record.shoes_task_id)
                and not record.is_pair
                and not record.is_assortment
            )

    def _get_pair_and_variants_sync(self):
        super()._get_pair_and_variants_sync()
        if self.intrastat_duty_id:
            country_id = self.intrastat_duty_id.country_id.id
            intrastat_id = self.intrastat_duty_id.intrastat_id.id

            self.product_tmpl_single_id.write(
                {
                    "intrastat_duty_id": self.intrastat_duty_id.id,
                    "hs_code": self.hs_code,
                    "country_of_origin": country_id,
                    "image_1920": self.image_1920,
                }
            )

            if self.shoes_pair_weight_id.id:
                for assortment in self.product_variant_ids:
                    assortment.write(
                        {
                            "intrastat_code_id": intrastat_id,
                            "intrastat_origin_country_id": country_id,
                        }
                    )

                for pair in self.product_tmpl_single_id.product_variant_ids:
                    pair.write(
                        {
                            "intrastat_code_id": intrastat_id,
                            "intrastat_origin_country_id": country_id,
                        }
                    )

    def create_shoe_pairs(self) -> Any:
        # 1) Ejecutamos el comportamiento original: creación de pares
        res = super().create_shoe_pairs()
        # 2) Tras crear las plantillas "single", propagamos shoes_last_id
        for record in self:
            if record.shoes_last_id and record.product_tmpl_single_id:
                record.product_tmpl_single_id.write(
                    {
                        "shoes_last_id": record.shoes_last_id.id,
                    }
                )
        return res
