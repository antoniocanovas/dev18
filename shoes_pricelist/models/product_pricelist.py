# Copyright 2023 Serincloud SL - Ingenieriacloud.com
from collections.abc import Iterable

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductPricelist(models.Model):
    _inherit = ["product.pricelist"]

    RECALCULATION_TYPE = [
        ("integer_5", "Integer rounded in 0 or 5"),
        ("integer_rounded", "Integer Rounded"),
        ("integer_up", "Integer UP"),
        ("integer_low", "Integer LOW"),
        ("5cent", "Integer rounded -5 cents"),
    ]

    MARKETING_DISCOUNT = [
        ("1cent", "Integer -1 cent"),
        ("5cent", "Integer -5 cents"),
    ]

    shoes_campaign_id = fields.Many2one(
        "project.project",
        string="Campaign",
        store=True,
        copy=False,
        ondelete="restrict",
        tracking=16,
    )
    pnt_campaign_filter_ids = fields.Many2many(
        "project.project",
        "pricelist_campaign_filter_rel",
        "pricelist_id",
        "campaign_id",
        string="Campañas",
        help="Filtra las líneas visibles en la tarifa según las campañas seleccionadas",
    )
    margin = fields.Float("Margin %", store=True, copy=True, tracking=16)
    dollar_exchange = fields.Monetary("Currency exchange")
    recalculation_type = fields.Selection(
        selection=RECALCULATION_TYPE, string="Recalculation type"
    )
    marketing_discount = fields.Selection(
        selection=MARKETING_DISCOUNT, string="Marketing discount"
    )

    product_tmpl_item_ids = fields.One2many(
        "product.pricelist.item",
        "pricelist_id",
        domain=[("applied_on", "=", "1_product")],
    )

    pnt_item_ids = fields.Many2many(
        "product.pricelist.item",
        string="Filtered Price Rules",
        compute="_compute_pnt_item_ids",
        help="Líneas de tarifa filtradas según las campañas seleccionadas",
    )

    @api.depends(
        "item_ids", "pnt_campaign_filter_ids", "item_ids.pnt_visible_by_campaign"
    )
    def _compute_pnt_item_ids(self) -> None:
        """
        Calcula las líneas de tarifa visibles según el filtro de campañas.

        Si no hay filtro de campañas, devuelve todas las líneas.
        Si hay filtro, devuelve solo las líneas con pnt_visible_by_campaign = True.
        """
        for record in self:
            if not record.pnt_campaign_filter_ids:
                # Sin filtro, mostrar todas las líneas
                record.pnt_item_ids = record.item_ids
            else:
                # Con filtro, mostrar solo las líneas visibles
                record.pnt_item_ids = record.item_ids.filtered(
                    lambda item: item.pnt_visible_by_campaign
                )

    @api.depends("write_date")
    def _get_pricelist_product_tmpl(self):
        templates = []
        for li in self.item_ids:
            if li.product_tmpl_id.id not in templates:
                templates.append(li.product_id.product_tmpl_id.id)
        self.product_tmpl_ids = [(6, 0, templates)]

    product_tmpl_ids = fields.Many2many(
        "product.template",
        string="Product templates",
        store=False,
        compute="_get_pricelist_product_tmpl",
    )

    # Función para actualizar tarifas de precio llamada desde la pestaña "Recalculation" en cada tarifa: # noqa: E501
    def campaign_pricelist_recalculation(self: Iterable["ProductPricelist"]):
        for record in self:
            # Borrar líneas de la tarifa especificada:
            lines = self.env["product.pricelist.item"].search(
                [
                    ("pricelist_id", "=", record.id),
                    "|",
                    ("product_tmpl_id.is_pair", "=", True),
                    ("product_tmpl_id.is_assortment", "=", True),
                ]
            )
            lines.unlink()

            # Buscar productos PAR de esta CAMPAÑA:
            pairs = self.env["product.template"].search(
                [
                    ("shoes_pair_campaign_ids", "in", record.shoes_campaign_id.id),
                    ("is_pair", "=", True),
                    ("product_tmpl_set_id", "!=", False),
                ]
            )

            # Cálculo de precio del par en función del cambio de moneda y margen:
            company_currency = self.env.company.currency_id
            pricelist_currency = record.currency_id
            for pair in pairs:
                # Moneda del fabricante de este producto y los impuestos en aduana:
                manufacturer_currency = (
                    pair.manufacturer_id.property_purchase_currency_id
                )
                tax_estimation = (
                    pair.exwork * pair.shoes_task_id.intrastat_duty_id.duty / 100
                )

                # Alerta de FABRICANTE SIN MONEDA DE COMPRA asignada:
                if manufacturer_currency.id is False:
                    raise UserError(
                        "Asigna una moneda de compra para el proveedor: "
                        + str(pair.manufacturer_id.name)
                    )

                # Alerta de PRODUCTO SIN COSTE EXWORK:
                if (pair.exwork == 0) or (pair.exwork < 0):
                    raise UserError("Producto sin coste EXWORK: " + str(pair.name))

                # EL CAMBIO DE MONEDA no aplica para los casos:
                # Tarifa en $, compramos en $, nosotros en €.
                # Tarifa, empresa y fabricante en la misma moneda.
                exchange = 1

                # Tarifa y empresa en misma moneda, fabricante en distinta; aplicar cambio de moneda:  # noqa: E501
                if (manufacturer_currency != company_currency) and (
                    pricelist_currency == company_currency
                ):
                    exchange = record.dollar_exchange

                # Precio por par incluyendo cambio de moneda, margen, intrastat y exwork: # noqa: E501
                price = (
                    exchange
                    * (pair.exwork + pair.shipping_price + tax_estimation)
                    * (1 + record.margin / 100)
                )

                # Ahora redondear en función del tipo seleccionado en el recálculo:
                rounded_price = 0
                if record.recalculation_type == "integer_rounded":
                    rounded_price = round(price)
                elif record.recalculation_type == "integer_low":
                    rounded_price = int(price)
                elif record.recalculation_type == "integer_up":
                    rounded_price = round(price + 0.5)
                elif record.recalculation_type == "integer_5":
                    rounded_price = round(price / 5) * 5

                if record.marketing_discount == "1cent":
                    rounded_price -= 0.01
                if record.marketing_discount == "5cent":
                    rounded_price -= 0.05

                # Crear líneas de tarifa para pares:
                self.env["product.pricelist.item"].create(
                    {
                        "product_tmpl_id": pair.id,
                        "display_applied_on": "1_product",
                        "compute_price": "fixed",
                        "fixed_price": rounded_price,
                    }
                )
                # Ahora con los surtidos:
                assortment = pair.product_tmpl_set_id
                for pp in assortment.product_variant_ids:
                    assortment_price = rounded_price * pp.pairs_count
                    self.env["product.pricelist.item"].create(
                        {
                            "product_tmpl_id": assortment.id,
                            "product_id": pp.id,
                            "display_applied_on": "1_product",
                            "compute_price": "fixed",
                            "fixed_price": assortment_price,
                        }
                    )
