# Copyright 2024 Punt Sistemes SL

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    pnt_sale_type_id = fields.Many2one(
        comodel_name="sale.order.type",
        string="Shipping Mark",
        store=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("pnt_sale_type_id"):
                continue
            sale_line_id = vals.get("sale_line_id")
            if sale_line_id:
                sol = self.env["sale.order.line"].browse(sale_line_id)
                vals["pnt_sale_type_id"] = sol.order_id.type_id.id or False
            else:
                order_id = vals.get("order_id")
                company = (
                    self.env["purchase.order"].browse(order_id).company_id
                    if order_id
                    else self.env.company
                )
                vals["pnt_sale_type_id"] = company.default_shippingmark_id.id or False
        return super().create(vals_list)

    def write(self, vals):
        if "product_qty" in vals and not self.env.context.get("from_sale_order_line"):
            for line in self:
                if line.sale_line_id:
                    raise UserError(
                        _(
                            "No puedes modificar la cantidad de '%s' directamente: "
                            "esta línea de compra está vinculada al pedido de venta %s.\n\n"
                            "Modifica la cantidad en la línea de venta correspondiente.",
                            line.product_id.display_name,
                            line.sale_line_id.order_id.name,
                        )
                    )
        return super().write(vals)
