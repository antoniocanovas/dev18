# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'

    shoes_sku_item_ids = fields.Many2many('shoes.product.sku.item', string='SKU Items', default=[(6,0,[1,2,3,4,5])])

    @api.constrains('shoes_sku_item_ids')
    def _ensure_unique_sku(self):
        if len(self.shoes_sku_item_ids.ids) != 5:
            raise UserError('Include all codes to ensure an unique SKU per product.')