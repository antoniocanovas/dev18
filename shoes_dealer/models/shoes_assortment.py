# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError


class ShoesAssortment(models.Model):
    _name = "shoes.assortment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Shoes Assortment"

    name = fields.Char(string="Nombre", required=True, store=True, copy=True)
    code = fields.Char(string="Code", required=True, store=True, copy=False)

    #    def _get_size_attribute(self):
    #        self.attribute_id = self.env.user.company_id.size_attribute_id.id
    attribute_id = fields.Many2one(
        "product.attribute",
        string="Size Attribute",
        store=False,
        default=lambda self: self.env.user.company_id.size_attribute_id,
    )
    line_ids = fields.One2many(
        "shoes.assortment.line", "assortment_id", string="Lines", store=True, copy=True
    )
    value_ids = fields.One2many(
        "product.attribute.value",
        "assortment_id",
        string="Attribute values",
        readonly=True,
    )

    @api.constrains("line_ids")
    def check_no_edit_if_value_ids(self):
        if self.value_ids.ids:
            raise UserError("Assortment can be modified if is assigned to an attribute")

    # Pares del SET, para chequear con listas de materiales:
    @api.depends("line_ids", "line_ids.quantity")
    def _get_shoes_set_pair_count(self):
        for record in self:
            record["pairs_count"] = sum(li.quantity for li in record.line_ids)

    pairs_count = fields.Integer(
        "Pairs", store=True, compute="_get_shoes_set_pair_count"
    )
