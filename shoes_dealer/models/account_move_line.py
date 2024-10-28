# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from collections import defaultdict

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Comercialmente en cada línea de pedido quieren saber cuántos pares se han facturado:
    @api.depends('product_id', 'quantity')
    def _get_shoes_invoice_line_pair_count(self):
        for record in self:
            record['pairs_count'] = record.product_id.pairs_count * record.quantity
    pairs_count = fields.Integer('Pairs', store=True, compute='_get_shoes_invoice_line_pair_count')

    # Precio por par según tarifa:
    @api.depends('product_id','price_unit')
    def _get_shoes_invoice_pair_price(self):
        for record in self:
            record.pair_price = record.price_subtotal / record.pairs_count if record.pairs_count else 0
    pair_price = fields.Float('Pair price', store=True, compute='_get_shoes_invoice_pair_price')

    color_value_id = fields.Many2one('product.attribute.value', string='Color',
                                         store=True,
                                         related='product_id.color_value_id')

    size_value_id = fields.Many2one('product.attribute.value', string='Size',
                                         store=True,
                                         related='product_id.size_value_id')

    shoes_campaign_id = fields.Many2one('project.project', string='Shoes Campaign',
                                        store=True,
                                        related='product_id.product_tmpl_id.shoes_campaign_id')
    shoes_model_id = fields.Many2one('product.template', store=True, related='product_id.shoes_model_id')
    exwork_single_euro = fields.Monetary(related="shoes_model_id.exwork_single_euro")

    @api.depends('price_subtotal', 'cost_price')
    def _get_shoes_margin(self):
        for record in self:
            # Chequeo de si es factura de cliente o abono:
            type = 1 if record.move_type == 'out_invoice' else -1
            record['shoes_margin'] = type * (record.price_subtotal - record.cost_price)

    shoes_margin = fields.Monetary('Margin', store=True, compute='_get_shoes_margin')

    #margen por par de zapatos, en caso de venta de surtido dividimos el margen total entre el número de pares
    @api.depends('shoes_margin', 'pairs_count')
    def _get_shoes_pair_margin(self):
        for record in self:
            shoes_pair_margin = record.shoes_pair_margin
            if record.pairs_count != 0:
                shoes_pair_margin = record.shoes_margin / record.pairs_count
            record['shoes_pair_margin'] = shoes_pair_margin

    shoes_pair_margin = fields.Monetary('Pair margin', store=True, compute='_get_shoes_pair_margin')

    #el precio de venta del par dividimos el total de la línea entre el número de pares, para considerar los descuentos.
    @api.depends("price_unit")
    def _get_pair_price_sale(self):
        for record in self:
            price_pair_sale = record.price_subtotal
            if (record.pairs_count != 0) and (record.quantity):
                price_pair_sale = price_pair_sale / record.pairs_count
            record['pair_price_sale'] = price_pair_sale
    pair_price_sale = fields.Monetary("Pair price sale", store=True, compute="_get_pair_price_sale")

    # Calcula el precio de costo en función del número de pares y el precio unitario
    @api.depends('exwork_single_euro', 'pairs_count')
    def _get_cost_price(self):
        for record in self:
            record.cost_price = record.pairs_count * record.exwork_single_euro if record.shoes_model_id.id else 0
    cost_price = fields.Float("Cost price", store=True, compute="_get_cost_price")

    # Calcula el descuento total aplicado en la línea de pedido
    @api.depends('discount','price_unit','quantity')
    def _get_total_shoes_discount(self):
        for record in self:
            # Chequeo de si es factura de cliente o abono:
            type = 1 if record.move_type == 'out_invoice' else -1
            record.discount_amount = type * (record.price_unit * record.quantity - record.price_subtotal)
    discount_amount = fields.Monetary("Total discount", store=True, compute="_get_total_shoes_discount")
