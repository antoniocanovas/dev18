# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"


    shoes_accesory_ids = fields.One2many(
        "shoes.accesory", "task_id",
        string="Accesories"
    )
