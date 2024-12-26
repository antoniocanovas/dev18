# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductPricelist(models.Model):
    _inherit = ["product.pricelist"]

    RECALCULATION_TYPE = [
        ("integer_rounded", "Integer Rounded"),
        ("integer_up", "Integer UP"),
    ]

    shoes_campaign_id = fields.Many2one("project.project", string="Campaign", store=True, copy=False, tracking=16)
    margin = fields.Float("Margin %", store=True, copy=True, tracking=16)
    dollar_exchange = fields.Monetary('Currency exchange')
    recalculation_type = fields.Selection(selection=RECALCULATION_TYPE, string='Recalculation type')

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
        self.product_tmpl_ids = [(6, 0, templates)]

    product_tmpl_ids = fields.Many2many(
        "product.template",
        string="Product templates",
        store=False,
        compute="_get_pricelist_product_tmpl",
    )

    # Función para actualizar tarifas de precio llamada desde la pestaña "Recalculation" en cada tarifa:
    def campaign_pricelist_recalculation(self):
        for record in self:
            # Borrar líneas de la tarifa especificada:
            lines = self.env['product.pricelist.item'].search([
                ('pricelist_id','=',record.id),
                ('product_tmpl_id.shoes_campaign_id','=',record.id)])
            lines.unlink()

            # Buscar productos PAR de esta CAMPAÑA:
            pairs = self.env['product.template'].search([
                ('shoes_campaign_id','=',record.id),
                ('is_pair','=',True)
            ])

            # Cálculo de precio del par en función del cambio de moneda y margen:


