from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    product_assortment_id = fields.Many2one(
        "shoes.assortment",
        string="Product Assortment",
        compute="_compute_product_assortment_id",
        store=True,
    )

    @api.depends("product_template_attribute_value_ids")
    def _compute_product_assortment_id(self):
        for product in self:
            assortment = False
            try:
                if product.product_tmpl_id:
                    assortment_attribute = (
                        self.env.user.company_id.assortment_attribute_id
                    )
                    if assortment_attribute:
                        attribute_values = self.env["product.attribute.value"].search(
                            [
                                ("attribute_id", "=", assortment_attribute.id),
                                ("assortment_id", "!=", False),
                            ]
                        )
                        product_attr_values = (
                            product.product_template_attribute_value_ids.mapped(
                                "product_attribute_value_id"
                            )
                        )
                        for attr_value in attribute_values:
                            if (
                                attr_value.assortment_id
                                and attr_value in product_attr_values
                            ):
                                assortment = attr_value.assortment_id
                                break
            except Exception:
                pass
            product.product_assortment_id = assortment
