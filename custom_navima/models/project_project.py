# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectProject(models.Model):
    _inherit = "project.project"


    # Secuencia para asignar los números de serie:
    tracking_sequence = fields.Integer('Next N/S', default=1)