# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    shoes_task_id = fields.Many2one('project.task', string='Shoes model')
    shoes_shape_id = fields.Many2one('shoes.shape', related='shoes_task_id.shoes_shape_id')