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
            if record.is_pair:
                amount = record.exwork_euro * (1 + duty_percent / 100)
            record.estimated_pair_landed_cost = amount

    @api.depends("exwork", "sale_margin","estimated_pair_landed_cost")
    def _compute_recommended_sale_price(self):
        super()._compute_recommended_sale_price()
        for product in self:
            amount = product.estimated_pair_landed_cost or 0.0
            amount += (
                (product.estimated_pair_landed_cost or 0.0) * product.sale_margin / 100
            )
            product.recommended_sale_price = amount

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
