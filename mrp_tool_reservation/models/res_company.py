# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


import logging

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    mrp_tool_reservation_stage_id = fields.Many2one(
        'maintenance.stage', string='MRP Tool stage',
        help='Stage used on MRP tools as maintenance to be reserved until finish production.'
    )
    mrp_tool_done_stage_id =  fields.Many2one(
        'maintenance.stage', string='MRP stage DONE',
        help='Stage used on MRP tools as maintenance to be DONE, remember configure as REQUEST DONE.'
    )
    mrp_tool_reservation_time = fields.Float('Reservation time')