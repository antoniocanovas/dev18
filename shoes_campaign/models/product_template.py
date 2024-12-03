# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api

class ProductTemplate(models.Model):
    _inherit = "product.template"

    shoes_task_id = fields.Many2one('project.task', string='Shoes model')
    shoes_last_id = fields.Many2one('shoes.last', related='shoes_task_id.shoes_last_id')