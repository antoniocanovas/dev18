from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    weight = fields.Float(string="Gross Weight", digits="Stock Weight")
    net_weight = fields.Float(string="Net Weight", digits="Stock Weight")
    volume = fields.Float(string="Volume", digits="Volume")
    width_length_high = fields.Char(string="W×L×H (cm)")
