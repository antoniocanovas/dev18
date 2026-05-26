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

    @api.depends("shoes_accesory_ids.subtotal")
    def _compute_exwork_accesory(self):
        for task in self:
            task.exwork_accesory = sum(task.shoes_accesory_ids.mapped("subtotal"))

    @api.depends("exwork_factory", "exwork_accesory", "exwork_accesory_tax_percent")
    def _compute_exwork(self):
        for task in self:
            accesory_total = task.exwork_accesory * (
                1 + task.exwork_accesory_tax_percent / 100
            )
            task.exwork = task.exwork_factory + accesory_total