# Copyright 2024 Punt Sistemes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ShoesProductCreationWizard(models.TransientModel):
    _name = "shoes.product.creation.wizard"
    _description = "Shoes product creation wizard"

    # Crear productos, proponiendo todos los restantes (deseleccionables) y
    # asignado a la línea el nuevo creado):
    name = fields.Char(related="task_id.name")
    task_id = fields.Many2one("project.task")

    shoes_campaign_id = fields.Many2one(related="task_id.project_id")
    manufacturer_id = fields.Many2one(related="task_id.manufacturer_id")

    shoes_model_material_ids = fields.One2many(
        related="task_id.shoes_model_material_ids"
    )
    material_ids = fields.Many2many("shoes.model.material", name="Model materials")

    def action_apply(self):
        for record in self:
            # Asignar nombre con códigos de fabricante y producto al final.
            for li in record.material_ids:
                name = record.task_id.name
                if record.manufacturer_id.ref and li.material_id.code:
                    name += "-" + record.manufacturer_id.ref + li.material_id.code
                elif not record.manufacturer_id.ref and li.material_id.code:
                    name += "-" + li.material_id.code
                elif record.manufacturer_id.ref and not li.material_id.code:
                    name += "-" + li.manufacturer_id.ref

                # Creación de productos:
                newproduct = (
                    self.env["product.template"]
                    .with_context(default_task_id=False, default_project_id=False)
                    .create(
                        {
                            "name": name,
                            "shoes_campaign_id": record.task_id.project_id.id,
                            "shoes_campaign_ids": [
                                (6, 0, [record.task_id.project_id.id])
                            ],
                            "product_brand_id": record.task_id.product_brand_id.id,
                            "manufacturer_id": record.manufacturer_id.id,
                            "gender": record.task_id.gender,
                            "shoes_pair_weight_id": (
                                record.task_id.shoes_pair_weight_id.id
                            ),
                            "material_id": li.material_id.id,
                            "shoes_last_id": li.shoes_last_id.id,
                            "shoes_task_id": record.task_id.id,
                            "type": "consu",
                            "is_storable": True,
                            "tracking": self.env.company.shoes_assortment_tracking,
                            "service_tracking": "no",
                            "product_add_mode": "matrix",
                            "intrastat_duty_id": record.task_id.intrastat_duty_id.id,
                            "intrastat_code_id": (
                                record.task_id.intrastat_duty_id.intrastat_id.id
                            ),
                            "intrastat_origin_country_id": (
                                record.task_id.intrastat_duty_id.country_id.id
                            ),
                            "hs_code": (
                                record.task_id.intrastat_duty_id.intrastat_id.code
                            ),
                            "country_of_origin": (
                                record.task_id.intrastat_duty_id.country_id.id
                            ),
                            "exwork": record.task_id.exwork,
                            "sale_margin": record.task_id.project_id.default_sale_margin
                            or 0.0,
                            "image_1920": record.task_id.displayed_image_id.datas,
                            "categ_id": record.task_id.product_categ_id.id,
                        }
                    )
                )
                li["shoes_product_tmpl_id"] = newproduct.id
