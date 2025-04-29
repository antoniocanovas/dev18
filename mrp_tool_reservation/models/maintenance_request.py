# Copyright Serincloud SL - Ingenieriacloud.com


from odoo import fields, models, api
from datetime import timedelta

class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    expected_close_date = fields.Datetime('Expected closing', store=True, compute='_get_expected_close_date')

    @api.depends('schedule_date','duration')
    def _get_expected_close_date(self):
        for request in self:
            if request.schedule_date and request.duration > 0:
                request.expected_close_date = request.schedule_date + timedelta(hours=request.duration)