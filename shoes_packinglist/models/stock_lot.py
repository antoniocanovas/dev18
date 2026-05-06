from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    weight = fields.Float(string="Gross Weight", digits="Stock Weight")
    net_weight = fields.Float(string="Net Weight", digits="Stock Weight")
    volume = fields.Float(string="Volume", digits="Volume")
    width_length_high = fields.Char(string="W×L×H (cm)")
    container_line_id = fields.Many2one(
        "purchase.container.line",
        string="Container Line",
        index=True,
        ondelete="set null",
    )
    container_id = fields.Many2one(
        "purchase.container",
        string="Container",
        related="container_line_id.container_id",
        store=True,
    )
