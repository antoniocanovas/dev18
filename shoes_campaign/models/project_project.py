# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    is_shoes_campaign = fields.Boolean("Is shoes campaign", default=True)

    # Datos comunes para creación de productos desde tareas:
    product_brand_id = fields.Many2one(
        "product.brand", string="Brand", ondelete="restrict"
    )
    task_code_prefix = fields.Char("Task prefix")
    task_code_sequence = fields.Integer("Next task code", default=1)

    display_name = fields.Char(
        string="Display name", compute="_compute_display_name", store=True
    )

    @api.depends("name", "product_brand_id")
    def _compute_display_name(self):
        for record in self:
            if record.name and record.product_brand_id.id:
                record.display_name = f"({record.product_brand_id.name}) {record.name}"
            elif record.name:
                record.display_name = record.name
            else:
                record.display_name = False

    def update_products_sale_margin(self):
        for record in self:
            if record.task_ids:
                products = record.task_ids.mapped('shoes_product_tmpl_id')
                products.write({'sale_margin': record.default_sale_margin})
        return True
