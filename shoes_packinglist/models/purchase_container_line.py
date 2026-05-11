from odoo import _, api, fields, models

_CHAR_FIELDS = [
    "shoes_campaign",
    "name",
    "color",
    "purchase_order",
    "assortment",
    "lot",
    "shippingmark",
]


class PurchaseContainerLine(models.Model):
    _name = "purchase.container.line"
    _description = "Purchase Container Packing List Line"
    _order = "container_id, id"
    _rec_name = "lot"

    container_id = fields.Many2one(
        "purchase.container",
        string="Container",
        required=True,
        ondelete="cascade",
        index=True,
    )
    shoes_campaign = fields.Char(string="Campaign")
    name = fields.Char(string="Product")
    color = fields.Char(string="Color")
    pairs = fields.Float(string="Pairs", digits="Product Unit of Measure")
    purchase_order = fields.Char(string="Purchase Order")
    assortment = fields.Char(string="Assortment")
    lot = fields.Char(string="Lot")
    volume = fields.Float(string="Volume", digits="Volume")
    pair_net_weight = fields.Float(string="Pair Net Weight", digits="Stock Weight")
    pair_gross_weight = fields.Float(string="Pair Gross Weight", digits="Stock Weight")
    assortment_net_weight = fields.Float(
        string="Assortment Net Weight", digits="Stock Weight"
    )
    assortment_gross_weight = fields.Float(
        string="Assortment Gross Weight", digits="Stock Weight"
    )
    shippingmark = fields.Char(string="Shipping Mark")
    high = fields.Float(string="High", digits="Volume")
    width = fields.Float(string="Width", digits="Volume")
    length = fields.Float(string="Length", digits="Volume")
    move_id = fields.Many2one(
        "stock.move",
        string="Stock Move",
        readonly=True,
        index=True,
        copy=False,
    )
    tariff_heading = fields.Char(string="Tariff Heading")
    currency_id = fields.Many2one(
        "res.currency",
        related="container_id.currency_id",
        string="Currency",
        store=False,
    )
    price = fields.Float(string="Price", digits="Product Price")
    client_order_ref = fields.Char(string="Client Order Ref")

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _clean_char_fields(vals)
        return super().create(vals_list)

    def write(self, vals):
        _clean_char_fields(vals)
        return super().write(vals)

    @api.depends("lot")
    def _compute_display_name(self):
        for record in self:
            record.display_name = record.lot or _("Container Line #%d") % record.id


def _clean_char_fields(vals):
    """Strip leading/trailing whitespace and tabs from all Char fields."""
    for field in _CHAR_FIELDS:
        if vals.get(field):
            vals[field] = vals[field].strip()
