# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from collections import defaultdict

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # Comercialmente en cada pedido quieren saber cuántos pares se han facturado:
    @api.depends('product_id', 'quantity')
    def _get_shoes_invoice_line_pair_count(self):
        for record in self:
            record['pairs_count'] = record.product_id.pairs_count * record.quantity
    pairs_count = fields.Integer('Pairs', store=True, compute='_get_shoes_invoice_line_pair_count')

    # Precio por par según tarifa:
    @api.depends('product_id','price_unit')
    def _get_shoes_invoice_pair_price(self):
        for record in self:
            total = 0
            if record.pairs_count != 0: total = record.price_subtotal / record.pairs_count
            record['pair_price'] = total
    pair_price = fields.Float('Pair price', store=True, compute='_get_shoes_invoice_pair_price')

    color_attribute_id = fields.Many2one('product.attribute.value', string='Color',
                                         store=True,
                                         related='product_id.color_attribute_id')

    size_attribute_id = fields.Many2one('product.attribute.value', string='Size',
                                         store=True,
                                         related='product_id.size_attribute_id')

    shoes_campaign_id = fields.Many2one('project.project', string='Shoes Campaign',
                                        store=True,
                                        related='product_id.product_tmpl_id.shoes_campaign_id')
    shoes_model_id = fields.Many2one('product.template', store=True, related='product_id.shoes_model_id')
    exwork_single_euro = fields.Monetary(related="shoes_model_id.exwork_single_euro")

    @api.depends('price_subtotal', 'cost_price')
    def _get_shoes_margin(self):
        for record in self:
            # Chequeo de si es factura de cliente o abono:
            if record.move_type == 'out_invoice': type = 1
            else: type = -1
            record['shoes_margin'] = type * (record.price_subtotal - record.cost_price
                                             - record.seller_commission - record.manager_commission)

    shoes_margin = fields.Monetary('Margin', store=True, compute='_get_shoes_margin')

    @api.depends('shoes_margin', 'pairs_count')
    def _get_shoes_pair_margin(self):
        for record in self:
            shoes_pair_margin = record.shoes_pair_margin
            if record.pairs_count != 0:
                shoes_pair_margin = record.shoes_margin / record.pairs_count
            record['shoes_pair_margin'] = shoes_pair_margin

    shoes_pair_margin = fields.Monetary('Pair margin', store=True, compute='_get_shoes_pair_margin')


    @api.depends("price_unit")
    def _get_pair_price_sale(self):
        for record in self:
            price_pair_sale = record.price_subtotal
            if (record.pairs_count != 0) and (record.quantity):
                price_pair_sale = price_pair_sale / record.pairs_count
            record['pair_price_sale'] = price_pair_sale
    pair_price_sale = fields.Monetary("Pair price sale", store=True, compute="_get_pair_price_sale")

    @api.depends('exwork_single_euro', 'pairs_count')
    def _get_cost_price(self):
        for record in self:
            cost = 0
            if record.shoes_model_id.id:
                cost = record.pairs_count * record.exwork_single_euro
            record.cost_price = cost
    cost_price = fields.Float("Cost price", store=True, compute="_get_cost_price")

    @api.depends('discount','price_unit','quantity')
    def _get_total_shoes_discount(self):
        for record in self:
            # Chequeo de si es factura de cliente o abono:
            if record.move_type == 'out_invoice': type = 1
            else: type = -1
            record['discount_amount'] = type * (record.price_unit * record.quantity - record.price_subtotal)
    discount_amount = fields.Monetary("Total discount", store=True, compute="_get_total_shoes_discount")


    seller_commission = fields.Monetary(
        string="Seller Commission",
        compute="_compute_account_move_line_seller_commission",
        store=True,
    )

    manager_commission = fields.Monetary(
        string="Manager Commission",
        compute="_compute_account_move_line_manager_commission",
        store=True,
    )

    @api.depends('move_id.payment_state')
    def _compute_account_move_line_seller_commission(self):
        for record in self:
            move = record.move_id
            if move.move_type in ['out_invoice', 'in_invoice']:
                sign = 1
                if not move.referrer_id:
                    continue
            else:
                sign = -1

            amount = 0
            rule = record._get_commission_rule()
            if rule:
                amount = move.currency_id.round(
                    record.price_subtotal * rule.rate / 100.0)
            # regulate commissions
            if rule.is_capped:
                amount = min(amount, rule.max_commission)
                # comm_by_rule[r] = amount

            record.seller_commission = sign * amount

    @api.depends('move_id.payment_state')
    def _compute_account_move_line_manager_commission(self):
                 for record in self:
                     move = record.move_id
                     if move.move_type in ['out_invoice', 'in_invoice']:
                         sign = 1
                         if not move.manager_id:
                             #record.manager_commission = record.manager_commission
                             continue
                     else:
                         sign = -1


                     amount = 0
                     rule = record._get_commission_manager_rule()
                     if rule:
                         amount = move.currency_id.round(
                             record.price_subtotal * rule.rate / 100.0)
                     # regulate commissions
                     if rule.is_capped:
                         amount = min(amount, rule.max_commission)
                         #comm_by_rule[r] = amount

                     record.manager_commission = sign * amount
