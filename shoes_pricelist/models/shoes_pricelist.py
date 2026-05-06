# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import api, fields, models

STATE = [
    ("draft", "Draft"),
    ("validation", "Validation"),
    ("done", "Done"),
]


class ShoesPricelist(models.Model):
    _name = "shoes.pricelist"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Shoes Pricelist"

    name = fields.Char("Name", compute="_get_name", store=True)
    shoes_campaign_id = fields.Many2one(
        "project.project", string="Campaign", required=True
    )
    pricelist_id = fields.Many2one(
        "product.pricelist", string="Pricelist", required=True
    )
    date = fields.Date(
        "Date", default=lambda self: fields.Date.context_today(self), required=True
    )
    active = fields.Boolean("Active", default=True)
    notes = fields.Html("Notes")
    line_ids = fields.One2many(
        "shoes.pricelist.line", "shoes_pricelist_id", string="Lines"
    )
    state = fields.Selection(
        selection=STATE,
        string="Status",
        store=True,
        copy=False,
        default="draft",
        tracking=100,
    )

    @api.depends("pricelist_id", "shoes_campaign_id")
    def _get_name(self):
        for record in self:
            name = ""
            if record.pricelist_id.id and record.shoes_campaign_id.id:
                name = record.shoes_campaign_id.name + " - " + record.pricelist_id.name
            record["name"] = name

    def update_shoes_pricelist(self):
        self.ensure_one()
        self.line_ids.unlink()
        models = self.env["product.template"].search(
            [
                ("is_pair", "=", True),
                ("shoes_pair_campaign_ids", "in", self.shoes_campaign_id.id),
            ]
        )

        for model in models:
            if model.product_variant_ids:
                product = model.product_variant_ids[0]
                pricelist_price = self.pricelist_id._get_product_price(
                    product=product,
                    quantity=1,
                    date=self.date,
                    uom_id=product.uom_id.id,
                )
            self.env["shoes.pricelist.line"].create(
                {
                    "shoes_pricelist_id": self.id,
                    "product_tmpl_single_id": model.id,
                    "pricelist_price": pricelist_price,
                }
            )
