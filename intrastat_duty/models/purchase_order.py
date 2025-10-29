# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _get_duty_estimation(self):
        for record in self:
            total = 0
            for li in record.order_line:
                if li.product_id.product_tmpl_id.intrastat_duty_id.id:
                    tax_percent = li.product_id.product_tmpl_id.intrastat_duty_id.duty / 100
                    total += li.product_qty * li.price_unit * tax_percent
            record['duty_estimation'] = total
    duty_estimation = fields.Monetary('Duty estimation', compute='_get_duty_estimation')