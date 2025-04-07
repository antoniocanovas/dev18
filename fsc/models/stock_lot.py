from odoo import _, api, fields, models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    base_lot_id = fields.Many2one('stock.lot', 'Base lot', compute='_get_base_lot_')
    parent_lot_id = fields.Many2one('stock.lot', 'Parent lot', compute='_get_parent_lot')
