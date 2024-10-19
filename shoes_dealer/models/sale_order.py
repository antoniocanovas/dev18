# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    # Comercialmente en cada pedido quieren saber cuántos pares se han vendido:
    def _get_shoes_pair_count(self):
        for record in self:
            count = 0
            for li in record.order_line:
                count += li.pairs_count
            record["pairs_count"] = count

    pairs_count = fields.Integer(
        string="Pairs", store=False, compute="_get_shoes_pair_count"
    )

    shoes_campaign_id = fields.Many2one(
        "project.project", string="Campaign", store=True, copy=True, tracking=10
    )

    @api.depends("shoes_campaign_id")
    def _get_campaign_top_sale(self):
        for record in self:
            models = self.env["product.template"].search(
                [
                    ("shoes_campaign_id", "=", record.shoes_campaign_id.id),
                    ("pairs_sold", ">", 1),
                ], limit=10
            )
            record["campaign_top_ids"] = [(6, 0, models.ids)]

    campaign_top_ids = fields.Many2many(
        "product.template", store=False, compute="_get_campaign_top_sale"
    )

    # Habilita o deshabilita la vista de pares más vendidos en las preferencias de usuario o desde botón en ventas:
    def _get_enabled_top_sales(self):
        self.top_sales = self.env.user.top_sales
    top_sales = fields.Boolean('Top sales', store=False, compute='_get_enabled_top_sales')
    def show_hide_top_sales(self):
        top_sales, user = False, self.env.user
        if user.top_sales == False:
            top_sales = True
        user.top_sales = top_sales


    # Restricción de validar pedidos de venta si tienen productos CUSTOM, primero crear compra para llevar línea:
    @api.constrains('state')
    def _check_no_custom_product_lines_without_purchase_order(self):
        for record in self:
            if record.state in ['sale']:
                for li in record.order_line:
                    if (li.product_id.is_assortment) and (not li.purchase_line_id.id) and (li.product_custom_attribute_value_ids):
                        raise UserError('Please, buy CUSTOM PRODUCTS before confirm, or personalized values will be lost.')


    def create_purchase_lines_for_custom_products(self):
        for record in self:
            for li in record.order_line:
                if (li.product_id.is_assortment) and (li.product_custom_attribute_value_ids.ids):
                    assortment_pair = li.product_custom_attribute_value_ids[0]
                    manufacturer = li.product_id.manufacturer_id
                    draft_purchases = self.env['purchase.order'].search([
                        ('partner_id', '=', manufacturer.id), ('state', '=', 'draft')])
                    if draft_purchases.ids:
                        po = draft_purchases[0]
                    else:   # Hay que crear un nuevo pedido
                        po = self.env['purchase.order'].create({'partner_id': manufacturer.id})
                    new_purchase_line = self.env['purchase.order.line'].create(
                        {'order_id': po.id, 'product_id': li.product_id.id, 'sale_line_id': li.id,
                         'product_qty': li.product_uom_qty, 'assortment_pair_id':assortment_pair.id})
                    # Indicar en SOL para que no vuelva a crear el pedido:
                    li['purchase_line_id'] = new_purchase_line.id
