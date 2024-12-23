# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"

    is_shoes_campaign = fields.Boolean('Is shoes campaign', related='project_id.is_shoes_campaign')

    # Datos comunes para creación de productos desde tareas:

    product_brand_id = fields.Many2one('product.brand', related='project_id.product_brand_id')
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')
    shoes_last_id = fields.Many2one('shoes.last', string='Last')
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

    shoes_model_material_ids = fields.One2many('shoes.model.material', 'task_id', string='Materials')
    pending_product_material_ids = fields.Many2many('product.material', string='Pending materials',
                                                    help='Pending product materials creation.')

    intrastat_duty_id = fields.Many2one('intrastat.duty', string='Duty estimation', copy=False)

    def create_shoe_model(self):
        if not self.shoes_product_tmpl_id.id:
            newproduct = self.env['product.template'].with_context(default_task_id=False, default_project_id=False).create({
                'name': self.name,
                'type': 'consu',
                'is_storable': True,
                'shoes_campaign_id': self.project_id.id,
                'shoes_campaign_ids':[(6,0,[self.project_id.id])],
                'product_brand_id':self.product_brand_id.id,
                'manufacturer_id':self.manufacturer_id.id,
                'gender': self.gender,
                'shoes_pair_weight_id': self.shoes_pair_weight_id.id,
                #'material_id': self.material_id.id,
                'shoes_task_id': self.id,
                'service_tracking': 'no',
                'intrastat_duty_id': self.intrastat_duty_id.id,
            })
            self.shoes_product_tmpl_id = newproduct.id

    @api.constrains('create_date')
    def task_code_sequence(self):
        prefix = self.project_id.task_code_prefix
        seq = self.project_id.task_code_sequence
        code = prefix + str(seq + 1000)[-3:]
        self.code = code
        self.project_id.task_code_sequence = seq +1