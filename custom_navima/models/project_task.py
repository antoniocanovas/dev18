# Copyright Custom Navima

from odoo import models


class ProjectTask(models.Model):
    _inherit = "project.task"
    _order = "priority desc, name asc"
