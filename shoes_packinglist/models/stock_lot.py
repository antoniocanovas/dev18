from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    weight = fields.Float(string="Gross Weight", digits="Stock Weight")
    net_weight = fields.Float(string="Net Weight", digits="Stock Weight")
    volume = fields.Float(string="Volume", digits="Volume")
    product_length = fields.Float(string="Length")
    product_height = fields.Float(string="Height")
    product_width = fields.Float(string="Width")
    dimensional_uom_id = fields.Many2one("uom.uom", string="Dimensional UoM")
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
