# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    is_shoes_campaign = fields.Boolean(
        "Is shoes campaign", related="project_id.is_shoes_campaign"
    )
    # Para componer el default_code del producto automáticamente:
    shoes_default_code_prefix = fields.Char("Internal ref. prefix")

    # Datos comunes para creación de productos desde tareas:

    product_brand_id = fields.Many2one(
        "product.brand", related="project_id.product_brand_id"
    )
    manufacturer_id = fields.Many2one(
        "res.partner", string="Manufacturer", ondelete="restrict"
    )
    code = fields.Char("Code")
    displayed_image = fields.Binary(related="displayed_image_id.datas")
    gender = fields.Selection(
        [("man", "Man"), ("woman", "Woman"), ("children", "Children")],
        string="Gender",
        copy=True,
        store=True,
    )

    shoes_pair_weight_id = fields.Many2one(
        "shoes.pair.weight", string="Pair Weight", default=False, ondelete="restrict"
    )
    intrastat_duty_id = fields.Many2one(
        "intrastat.duty", string="Duty estimation", copy=False, ondelete="restrict"
    )

    # Para filtro en domain de la creación de productos (wizard):
    shoes_model_material_ids = fields.One2many(
        "shoes.model.material", "task_id", string="Materials"
    )
    # Para pasar valor por defecto a líneas de materiales:
    shoes_default_last_id = fields.Many2one(
        "shoes.last", string="Default last", ondelete="restrict"
    )

    @api.constrains("create_date")
    def task_code_sequence(self):
        for rec in self:
            if not rec.code:
                prefix = rec.project_id.task_code_prefix
                seq = rec.project_id.task_code_sequence
                code = prefix + str(seq + 1000)[-3:]
                rec.code = code
                rec.project_id.task_code_sequence = seq + 1

    # Datos adicionales ¿modelo o producto?:
    shoes_material_main_id = fields.Many2one(
        "product.material", string="Main", ondelete="restrict"
    )
    shoes_material_external1_id = fields.Many2one(
        "product.material", string="External 1", ondelete="restrict"
    )
    shoes_material_external1_percent = fields.Float("External 1 (%)")
    shoes_material_external2_id = fields.Many2one(
        "product.material", string="External 2", ondelete="restrict"
    )
    shoes_material_external2_percent = fields.Float("External 2 (%)")
    shoes_material_lin_internal1_id = fields.Many2one(
        "product.material", string=" Internal Lin 1", ondelete="restrict"
    )
    shoes_material_lin_internal1_percent = fields.Float("Internal lin 1 (%)")
    shoes_material_lin_internal2_id = fields.Many2one(
        "product.material", string=" Internal Lin 2", ondelete="restrict"
    )
    shoes_material_lin_internal2_percent = fields.Float("Internal lin 2 (%)")
    shoes_closure_id = fields.Many2one(
        "shoes.closure", string="Closure", ondelete="restrict"
    )
    shoes_height = fields.Float("Shalft height")
    shoes_shalft_categ = fields.Selection(
        [("long", "Long"), ("half", "Half"), ("lower", "Lower")], string="Shaft type"
    )
    shoes_type = fields.Many2one("shoes.type", string="Type")
    shoes_with = fields.Char("With", translate=True)
    exwork = fields.Float("Exwork", store=True, copy=True, tracking=10)

    product_categ_id = fields.Many2one('product.category', string="Category")

    @api.depends("manufacturer_id")
    def _get_exwork_currency(self):
        for record in self:
            if (
                record.manufacturer_id.id
                and record.manufacturer_id.property_purchase_currency_id.id
            ):
                currency = record.manufacturer_id.property_purchase_currency_id.id
            elif (
                record.manufacturer_id.id
                and not record.manufacturer_id.property_purchase_currency_id.id
            ):
                currency = self.env.company.currency_id.id
            else:
                currency = self.env.user.company_id.exwork_currency_id.id
            record["exwork_currency_id"] = currency

    exwork_currency_id = fields.Many2one("res.currency", compute="_get_exwork_currency")
