# Copyright 2024 Punt Sistemes SL

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    sale_type = fields.Many2one(
        string="Default Shipping Mark",
    )

    shoes_shippingmark_ids = fields.Many2many(
        comodel_name="sale.order.type",
        string="Exclusive Shipping Marks",
        help="If empty, this customer can be served with any Shipping Mark. "
             "If filled, only the included ones will be allowed.",
    )

    @api.onchange("is_company")
    def _onchange_is_company_default_shippingmark(self):
        for partner in self:
            if partner.is_company and not partner.sale_type:
                partner.sale_type = self.env.company.default_shippingmark_id

    @api.model_create_multi
    def create(self, vals_list):
        default_sm = self.env.company.default_shippingmark_id
        if default_sm:
            for vals in vals_list:
                if vals.get("is_company") and not vals.get("sale_type"):
                    vals["sale_type"] = default_sm.id
        return super().create(vals_list)
