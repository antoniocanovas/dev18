# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = "project.project"

    is_shoes_campaign = fields.Boolean('Is shoes campaign', default=True)

    # Datos comunes para creación de productos desde tareas:
    product_brand_id = fields.Many2one('product.brand', string="Brand")
    task_code_prefix = fields.Char('Task prefix')
    task_code_sequence = fields.Integer('Next task code', default=1)