# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductPricelist(models.Model):
    _inherit = ["product.pricelist"]

    shoes_campaign_id = fields.Many2one("project.project", string="Campaign", store=True, copy=False, tracking=16)
    margin = fields.Float("Margin %", store=True, copy=True, tracking=16)
    currency_exchange = fields.Monetary('Currency exchange')

    # Función para actualizar tarifasde precio:
    def _update_campaign_pricelist(self):
        return True


    product_tmpl_item_ids = fields.One2many(
        "product.pricelist.item",
        "pricelist_id",
        domain=[("applied_on", "=", "1_product")],
    )

    @api.depends("item_ids")
    def _get_pricelist_product_tmpl(self):
        templates = []
        for li in self.item_ids:
            if li.product_tmpl_id.id not in templates:
                templates.append(li.product_id.product_tmpl_id.id)
        self.pnt_product_tmpl_ids = [(6, 0, templates)]

    product_tmpl_ids = fields.Many2many(
        "product.template",
        string="Product templates",
        store=False,
        compute="_get_pricelist_product_tmpl",
    )

    def products_pricelist_recalculation_by_campaign(self):
        for record in self:
            if record.id == self.env.company.retail_pricelist_id.id:
                record.item_ids.unlink()

                pares = self.env["product.template"].search(
                    [
                        ("product_tmpl_set_id", "!=", False),
                        ("shoes_campaign_id", "=", record.pnt_campaign_id.id),
                        ("product_brand_id", "=", record.pnt_product_brand_id.id),
                    ]
                )
                for p in pares:
                    precio = p.retail_price
                    newline = self.env["product.pricelist.item"].create(
                        {
                            "pricelist_id": record.id,
                            "product_tmpl_id": p.id,
                            "compute_price": "fixed",
                            "applied_on": "1_product",
                            "fixed_price": precio,
                        }
                    )

                    surtido = p.product_tmpl_set_id
                    for pp in surtido.product_variant_ids:
                        newline = self.env["product.pricelist.item"].create(
                            {
                                "pricelist_id": record.id,
                                "product_id": pp.id,
                                "compute_price": "fixed",
                                "applied_on": "0_product_variant",
                                "fixed_price": precio * pp.pairs_count,
                            }
                        )
            else:
                # Pares sueltos (tarifa por plantilla de producto):
                pairs = self.env["product.product"].search(
                    [
                        ("product_tmpl_set_id", "!=", False),
                        ("shoes_campaign_id", "=", record.pnt_campaign_id.id),
                        ("product_brand_id", "=", record.pnt_product_brand_id.id),
                    ]
                )

                pair_templates = []
                pre_margin = record.pnt_pre_margin_amount
                landed = record.pnt_landed_amount
                margin = record.pnt_margin
                post_margin = record.pnt_post_margin_amount

                # Pricelist item deletion to avoid old prices of pairs changed of campaign:
                lines = self.env["product.pricelist.item"].search(
                    [
                        ("pricelist_id", "=", record.id),
                        ("pnt_brand_id", "=", record.pnt_product_brand_id.id),
                        (
                            "product_tmpl_id.shoes_campaign_id",
                            "=",
                            record.pnt_campaign_id.id,
                        ),
                    ]
                )
                lines.unlink()

                for pr in pairs:
                    price = pr.lst_price
                    pr.write({"standard_price": pr.exwork + pr.shipping_price})
                    gross_price = round(
                        (
                            (price + pre_margin + landed) * (1 + margin / 100)
                            + post_margin
                        ),
                        2,
                    )

                    # Redondeo a 5 centimos, siempre al alza (hay que hacerlo con 2 round porque hace cosas raras):
                    cents = round((gross_price - int(gross_price)), 2)
                    cent = round(cents * 10 - int(cents * 10), 1)
                    if cent in [0, 0.5]:
                        addition = 0
                    elif cent < 0.5:
                        addition = 0.05 - cent / 10
                    else:
                        addition = 0.1 - cent / 10
                    rounded_price = gross_price + addition

                    if pr.product_tmpl_id.id not in pair_templates:
                        # Creamos una línea nueva:
                        pricelist_line = self.env["product.pricelist.item"].create(
                            {
                                "pricelist_id": record.id,
                                "product_tmpl_id": pr.product_tmpl_id.id,
                                "compute_price": "fixed",
                                "applied_on": "1_product",
                                "product_id": False,
                                "fixed_price": rounded_price,
                            }
                        )

                        # Añadimos al array para que no escriba lo mismo:
                        pair_templates.append(pr.product_tmpl_id.id)

                # Surtidos (tarifa por producto):
                sets = self.env["product.product"].search(
                    [
                        ("product_tmpl_single_id", "!=", False),
                        ("shoes_campaign_id", "=", record.pnt_campaign_id.id),
                        ("product_brand_id", "=", record.pnt_product_brand_id.id),
                    ]
                )
                for pr in sets:
                    product_bom = self.env["mrp.bom"].search(
                        [("product_id", "=", pr.id)]
                    )
                    if not product_bom.bom_line_ids.ids:
                        message = (
                            pr.name
                            + " has no Bill of Materials, please review and press CREATE PAIRS"
                        )
                        raise UserError(message)

                    # Crear líneas de tarifa:
                    single_price = (
                        pr.product_tmpl_single_id.list_price
                    )  # Utilizar standard_price
                    gross_price = round(
                        (
                            (single_price + pre_margin + landed) * (1 + margin / 100)
                            + post_margin
                        ),
                        2,
                    )

                    # Redondeo a 5 centimos, siempre al alza (hay que hacerlo con 2 round porque hace cosas raras):
                    cents = round((gross_price - int(gross_price)), 2)
                    cent = round(cents * 10 - int(cents * 10), 1)
                    if cent in [0, 0.5]:
                        addition = 0
                    elif cent < 0.5:
                        addition = 0.05 - cent / 10
                    else:
                        addition = 0.1 - cent / 10
                    rounded_price = (gross_price + addition) * pr.pairs_count

                    # Creamos una línea nueva:
                    pricelist_line = self.env["product.pricelist.item"].create(
                        {
                            "pricelist_id": record.id,
                            "product_tmpl_id": pr.product_tmpl_id.id,
                            "product_id": pr.id,
                            "compute_price": "fixed",
                            "applied_on": "0_product_variant",
                            "fixed_price": rounded_price,
                        }
                    )
