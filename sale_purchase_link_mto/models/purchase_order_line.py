# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        related='sale_line_id.order_id.partner_id',
        store=True,
        readonly=True,
        help="Customer from the original sale order that generated this purchase line"
    )
