# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    shoes_accesory_ids = fields.One2many(
        "shoes.accesory", "task_id",
        string="Accesories"
    )

    exwork_factory = fields.Float(
        "Exwork factory", store=True, copy=True, digits="Product Price"
    )
    exwork_accesory = fields.Float(
        "Exwork accesory",
        store=True,
        compute="_compute_exwork_accesory",
        digits="Product Price",
    )
    exwork_accesory_tax_percent = fields.Float(
        "Accesory duties %",
        help="Porcentaje de portes y aduanas en accesorios",
    )
    exwork = fields.Float(
        "Exwork",
        store=True,
        copy=True,
        tracking=10,
        compute="_compute_exwork",
        digits="Product Price",
    )

    @api.depends(
        "shoes_accesory_ids.subtotal", "shoes_accesory_ids.color_ids",
        "shoes_color_chart_item_ids", "shoes_chart_item_used_ids",
    )
    def _compute_exwork_accesory(self):
        for task in self:
            common = sum(acc.subtotal for acc in task.shoes_accesory_ids if not acc.color_ids)
            colored_lines = task.shoes_accesory_ids.filtered(lambda a: a.color_ids)
            all_color_items = task.shoes_color_chart_item_ids | task.shoes_chart_item_used_ids
            total_colors = len(all_color_items)
            if total_colors and colored_lines:
                colored = sum(acc.subtotal * len(acc.color_ids) for acc in colored_lines)
                task.exwork_accesory = common + colored / total_colors
            else:
                task.exwork_accesory = common + sum(colored_lines.mapped("subtotal"))

    @api.depends("exwork_factory", "exwork_accesory", "exwork_accesory_tax_percent")
    def _compute_exwork(self):
        for task in self:
            accesory_total = task.exwork_accesory * (
                1 + task.exwork_accesory_tax_percent / 100
            )
            task.exwork = task.exwork_factory + accesory_total