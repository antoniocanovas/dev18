# Copyright Serincloud SL - Ingenieriacloud.com


from odoo import fields, models, api

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    tool_ids = fields.Many2many('maintenance.equipment', string='Compatible Tools')
