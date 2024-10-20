# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"

    is_shoes_campaign = fields.Boolean('Is shoes campaign', related='project_id.is_shoes_campaign')

    # Datos comunes para creación de productos desde tareas:

    product_brand_id = fields.Many2one('product.brand', related='project_id.product_brand_id')
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')
    shoes_shape_id = fields.Many2one('shoes.shape', string='Shape')
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
    shoes_hscode_id = fields.Many2one(
        "shoes.hs.code", string="Shoes HS Code", default=False
    )

    material_id = fields.Many2one(
        "product.material", string="Material", store=True, copy=True
    )

    shoes_product_tmpl_id = fields.Many2one('product.template', string="Product")

    def create_shoe_model(self):
        if not self.shoes_product_tmpl_id.id:
            newproduct = self.env['product.template'].create({
                'name': self.name,
                'type': 'consu',
                'service_tracking': False,
                'shoes_campaign_id':self.project_id.id,
                'product_brand_id':self.product_brand_id.id,
                'manufacturer_id':self.manufacturer_id.id,
                'gender': self.gender,
                'shoes_pair_weight_id': self.shoes_pair_weight_id.id,
                'shoes_hscode_id': self.shoes_hscode_id.id,
                'material_id': self.material_id.id,
                'shoes_task_id': self.id,
            })
            self.shoes_product_tmpl_id = newproduct.id

    @api.constrains('create_date')
    def task_code_sequence(self):
        prefix = self.project_id.task_code_prefix
        seq = self.project_id.task_code_sequence
        code = prefix + str(seq + 1000)[-3:]
        self.code = code
        self.project_id.task_code_sequence = seq +1