# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = "project.task"

    is_shoes_campaign = fields.Boolean(
        "Is shoes campaign", related="project_id.is_shoes_campaign"
    )

    project_ribbon_label = fields.Char(compute='_compute_project_ribbon_label')

    @api.depends('project_id')
    def _compute_project_ribbon_label(self):
        active_id = self.env.context.get('active_id')
        for task in self:
            if task.project_id and active_id and task.project_id.id != active_id:
                task.project_ribbon_label = task.project_id.name
            else:
                task.project_ribbon_label = False

    # Para componer el default_code del producto automáticamente:
    shoes_default_code_prefix = fields.Char("Internal ref. prefix")

    shoes_default_code_sufix = fields.Char(
        "Internal ref. sufix",
        readonly=False,
        store=True,
        compute="_get_shoes_default_code_sufix"
    )
    @api.depends('project_id.name')
    def _get_shoes_default_code_sufix(self):
        for record in self:
            name = record.env.company.shoes_sufix_model_code_prefix or ""
            if record.project_id.id and record.project_id.name:
                name += record.project_id.name
            record.shoes_default_code_sufix = name

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

    product_categ_id = fields.Many2one("product.category", string="Category")

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

    # Refactorización model-material para individual por tarea:
    shoes_model_material = fields.Char(
       "Model material",
       compute="_get_shoes_model_material",
       store=True
    )
    shoes_manufacturer_ref = fields.Char("Manufacturer Ref")
    shoes_material_id = fields.Many2one(
       "product.material", string="Material", ondelete="restrict"
    )
    shoes_last_id = fields.Many2one("shoes.last", string="Last", ondelete="restrict")
    trade_name = fields.Char(
        "Trade Name",
        help="Nombre comercial utilizado para exportación de datos",
    )
    shoes_product_tmpl_id = fields.Many2one("product.template", string="Product")

    sale_campaign_ids = fields.Many2many(
        "project.project",
        compute="_compute_sale_campaign_ids",
        store=True,
        string="Sale Campaigns",
    )

    @api.depends("project_id", "shoes_product_tmpl_id.shoes_campaign_ids")
    def _compute_sale_campaign_ids(self):
        for task in self:
            task.sale_campaign_ids = (
                task.shoes_product_tmpl_id.shoes_campaign_ids | task.project_id
            )
    # Para añadir QR en tarifas:
    shoes_url = fields.Char("URL")


    @api.depends("shoes_material_id", "shoes_manufacturer_ref", "shoes_default_code_prefix")
    def _get_shoes_model_material(self):
       for record in self:
           name = ""
           if record.shoes_default_code_prefix:
               name += record.shoes_default_code_prefix
           if record.shoes_material_id.code:
               name += record.shoes_material_id.code
           if record.manufacturer_id.ref:
               name += record.manufacturer_id.ref
           record["shoes_model_material"] = name


    # Creación de producto desde tarea:
    def shoes_create_product(self):
        if not self.env.company.shoes_pair_uom_id or not self.env.company.shoes_assortment_uom_id:
            raise UserError(_(
                "Pide a tu administrador que parametrice las unidades "
                "para pares sueltos y surtidos en la configuración de "
                "la compañía."
            ))
        for record in self:
            # Asignar nombre con códigos de fabricante y producto al final.
            name = record.name
            if record.manufacturer_id.ref and record.shoes_material_id.code:
                name += "-" + record.manufacturer_id.ref + record.shoes_material_id.code
            elif not record.manufacturer_id.ref and record.shoes_material_id.code:
                name += "-" + record.shoes_material_id.code
            elif record.manufacturer_id.ref and not record.shoes_material_id.code:
                name += "-" + record.manufacturer_id.ref

            # Creación de productos:
            newproduct = (
                self.env["product.template"]
                .with_context(default_task_id=False, default_project_id=False)
                .create(
                    {
                        "name": name,
                        "shoes_campaign_id": record.project_id.id,
                        "shoes_campaign_ids": [
                            (6, 0, [record.project_id.id])
                        ],
                        "product_brand_id": record.product_brand_id.id,
                        "manufacturer_id": record.manufacturer_id.id,
                        "gender": record.gender,
                        "shoes_pair_weight_id": (
                            record.shoes_pair_weight_id.id
                        ),
                        "material_id": record.shoes_material_id.id,
                        "shoes_last_id": record.shoes_last_id.id,
                        "shoes_task_id": record.id,
                        "type": "consu",
                        "is_storable": True,
                        "uom_id": self.env.company.shoes_assortment_uom_id.id or False,
                        "uom_po_id": self.env.company.shoes_assortment_uom_id.id or False,
                        "tracking": self.env.company.shoes_assortment_tracking,
                        "service_tracking": "no",
                        "product_add_mode": "matrix",
                        "exwork": record.exwork,
                        "sale_ok": False,
                        "sale_margin": record.project_id.default_sale_margin
                        or 0.0,
                        "image_1920": record.displayed_image_id.datas,
                        "categ_id": record.product_categ_id.id,
                    }
                )
            )
            record["shoes_product_tmpl_id"] = newproduct.id
            # Intrastat fields require at least one variant to exist (constraint);
            # write them after create so the default variant is already present.
            if record.intrastat_duty_id:
                newproduct.write({
                    "intrastat_duty_id": record.intrastat_duty_id.id,
                    "intrastat_code_id": record.intrastat_duty_id.intrastat_id.id,
                    "intrastat_origin_country_id": record.intrastat_duty_id.country_id.id,
                    "hs_code": record.intrastat_duty_id.intrastat_id.code,
                    "country_of_origin": record.intrastat_duty_id.country_id.id,
                })
