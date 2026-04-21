# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    estimated_pair_landed_cost = fields.Monetary(
        "Pair landed cost €",
        help="Estimated pair landed cost, based on intrastat duty.",
        compute="_get_estimated_pair_landed_cost",
    )

    # Calcula el valor de estimated_pair_landed_cost basado en la moneda y duty
    # estimation:
    @api.depends("exwork_single", "intrastat_duty_id")
    def _get_estimated_pair_landed_cost(self):
        for record in self:
            amount = 0
            duty_percent = (
                record.intrastat_duty_id.duty if record.intrastat_duty_id else 0.0
            )
            if record.is_assortment:
                amount = record.exwork_single_euro * (1 + duty_percent / 100)
            elif record.is_pair:
                amount = record.exwork_euro * (1 + duty_percent / 100)
            record.estimated_pair_landed_cost = amount

    @api.depends("exwork", "sale_margin", "exwork_euro", "exwork_single_euro", "intrastat_duty_id")
    def _compute_recommended_sale_price(self):
        super()._compute_recommended_sale_price()
        for product in self:
            # Para productos normales el super() ya calcula correctamente.
            # Solo sobreescribir para surtido y par usando landed cost + margen.
            if not product.is_assortment and not product.is_pair:
                continue
            duty_percent = product.intrastat_duty_id.duty if product.intrastat_duty_id else 0.0
            if product.is_assortment:
                base = product.exwork_single_euro * (1 + duty_percent / 100)
            else:
                base = product.exwork_euro * (1 + duty_percent / 100)
            product.recommended_sale_price = base + base * product.sale_margin / 100

    @api.onchange("sale_margin", "exwork")
    def _onchange_recommended_price_intrastat(self):
        for record in self:
            if record.is_assortment or record.is_pair:
                duty_percent = (
                    record.intrastat_duty_id.duty if record.intrastat_duty_id else 0.0
                )
                if record.is_assortment:
                    base = record.exwork_single_euro * (1 + duty_percent / 100)
                else:
                    base = record.exwork_euro * (1 + duty_percent / 100)
                record.recommended_sale_price = base + base * record.sale_margin / 100

    @api.onchange("intrastat_duty_id")
    def _sync_intrastat_duty(self):
        # Prevenir bucle infinito usando contexto
        if self.env.context.get("skip_intrastat_sync"):
            return

        for record in self:
            intrastat_id = record.intrastat_duty_id.id

            # Actualizar product_tmpl_set_id solo si es diferente
            if (
                record.product_tmpl_set_id.id
                and record.product_tmpl_set_id.intrastat_duty_id.id != intrastat_id
            ):
                record.product_tmpl_set_id.with_context(
                    skip_intrastat_sync=True
                ).intrastat_duty_id = intrastat_id

            # Actualizar product_tmpl_single_id solo si es diferente
            if (
                record.product_tmpl_single_id.id
                and record.product_tmpl_single_id.intrastat_duty_id.id != intrastat_id
            ):
                record.product_tmpl_single_id.with_context(
                    skip_intrastat_sync=True
                ).intrastat_duty_id = intrastat_id
