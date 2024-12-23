# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"

    is_shoes_campaign = fields.Boolean('Is shoes campaign', related='project_id.is_shoes_campaign')

    # Datos comunes para creación de productos desde tareas:

    product_brand_id = fields.Many2one('product.brand', related='project_id.product_brand_id')
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')
    code = fields.Char('Code')
    gender = fields.Selection(
        [("man", "Man"), ("woman", "Woman"), ("unisex", "Unisex")],
        string="Gender",
        copy=True,
        store=True,
    )

    shoes_pair_weight_id = fields.Many2one(
        "shoes.pair.weight", string="Pair Weight", default=False
    )
    intrastat_duty_id = fields.Many2one('intrastat.duty', string='Duty estimation', copy=False)

    # Para filtro en domain de la creación de productos (wizard):
    shoes_model_material_ids = fields.One2many('shoes.model.material', 'task_id', string='Materials')

    @api.constrains('create_date')
    def task_code_sequence(self):
        prefix = self.project_id.task_code_prefix
        seq = self.project_id.task_code_sequence
        code = prefix + str(seq + 1000)[-3:]
        self.code = code
        self.project_id.task_code_sequence = seq +1

    # Datos adicionales ¿modelo o producto?:
    shoes_material_main_id = fields.Many2one('product.material', string='Main')
    shoes_material_external1_id = fields.Many2one('product.material', string='External 1')
    shoes_material_external1_percent = fields.Float('External 1 (%)')
    shoes_material_external2_id = fields.Many2one('product.material', string='External 2')
    shoes_material_external2_percent = fields.Float('External 2 (%)')
    shoes_material_lin_internal1_id = fields.Many2one('product.material', string=' Internal Lin 1')
    shoes_material_lin_internal1_percent = fields.Float('Internal lin 1 (%)')
    shoes_material_lin_internal2_id = fields.Many2one('product.material', string=' Internal Lin 2')
    shoes_material_lin_internal2_percent = fields.Float('Internal lin 2 (%)')
    shoes_closure_id = fields.Many2one('shoes.closure', string='Closure')
    shoes_height = fields.Float('Shalft height')
    shoes_shalft_categ = fields.Selection([('long','Long'),('half','Half'),('lower','Lower')], string='Shaft type')
    shoes_type = fields.Many2one('shoes.type', string='Type')
    shoes_with = fields.Char('With', translate=True)
