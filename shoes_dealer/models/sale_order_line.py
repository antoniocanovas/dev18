# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError, ValidationError

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    referrer_id = fields.Many2one(
        "res.partner", related="order_id.referrer_id", store=True
    )

    purchase_line_id = fields.Many2one("purchase.order.line", string="Purchase line")

    # Comercialmente en cada pedido quieren saber cuántos pares se han vendido:
    @api.depends("product_id", "product_uom_qty", "custom_assortment_pairs")
    def _get_shoes_sale_line_pair_count(self):
        for record in self:
            total = 0
            if record.product_custom_attribute_value_ids.ids:
                total = record.custom_assortment_pairs * record.product_uom_qty
            else:
                total = record.product_id.pairs_count * record.product_uom_qty
            record["pairs_count"] = total

    pairs_count = fields.Integer(
        "Pairs", store=True, compute="_get_shoes_sale_line_pair_count"
    )

    @api.depends('write_date')
    def _get_custom_assortment_pairs(self):
        for record in self:
            pairs_count = 0
            if record.product_id.is_assortment and record.name and record.product_custom_attribute_value_ids.ids:
                customvalue = record.product_custom_attribute_value_ids[0].custom_value
                # Quitar espacios del campo custom del surtido:
                customvalue = customvalue.replace(" ", "").lower()
                customvalues = customvalue.split(",")
                for li in customvalues:
                    element = li.split("x")
                    pairs_count += int(element[1])
            record.custom_assortment_pairs = pairs_count
    custom_assortment_pairs = fields.Integer("Custom assortment pairs", store=True,
                                             compute='_get_custom_assortment_pairs')

    @api.depends('write_date')
    def _get_assortment_pair(self):
        for record in self:
            customvalue, cleanvalues, sizes, pairs, pair_products, pairs_count = "", "", "", "", "", 0
            if record.product_id.is_assortment and record.name:
                if record.product_custom_attribute_value_ids.ids:
                    customvalue =  record.product_custom_attribute_value_ids[0].custom_value
                    if customvalue:
                        # Quitar espacios del campo custom del surtido:
                        customvalue = customvalue.replace(" ", "").lower()
                        customvalues = customvalue.split(",")
                        for li in customvalues:
                            element = li.split("x")
                            # Para tallas (encontrar si existe la talla y color en el par):
                            color_attribute_value_id = record.product_id.color_attribute_id
                            size_attribute = self.env.company.size_attribute_id
                            size_attribute_value_id = self.env['product.attribute.value'].search(
                                [('attribute_id', '=', size_attribute.id), ('name', '=', element[0])])

                            pppair = self.env['product.product'].search([('color_attribute_id', '=', color_attribute_value_id.id),
                                                                         ('size_attribute_id', '=', size_attribute_value_id.id),
                                                                         ('product_tmpl_id', '=', record.product_id.product_tmpl_single_id.id)])
                            sizes += element[0] + ","
                            pairs += element[1] + ","
                            pair_products += str(pppair.id) + ","

                        # OK, guardamos valores, tras quitar la última coma:
                        if len(sizes) > 0: sizes = sizes[:-1]
                        if len(pairs) > 0: pairs = pairs[:-1]
                        if len(pair_products) > 0: pair_products = pair_products[:-1]

                        cleanvalues = sizes + ";" + pairs + ";" + pair_products

                # Caso de un surtido normal (no custom) con ldm:
                elif not customvalue and record.product_id.bom_ids.ids:
                    bom = record.product_id.bom_ids[0]
                    cleanvalues = bom.assortment_pair
            record['assortment_pair'] = cleanvalues
    assortment_pair = fields.Char('Assortment pairs', compute='_get_assortment_pair')

    # Precio especial del para en la línea de ventas, recalculará precio unitario del producto surtido:
    special_pair_price = fields.Monetary("SPP", help="Special pair price")

    @api.onchange("special_pair_price")
    def _update_price_unit_from_spp(self):
        for record in self:
            record["price_unit"] = (
                    record.pairs_count * record.special_pair_price / record.product_uom_qty
            )

    # Para informes:
    state_id = fields.Many2one(
        "res.country.state",
        "Customer State",
        readonly=True,
        store=True,
        related="order_partner_id.state_id",
    )

    country_id = fields.Many2one(
        "res.country",
        "Customer Country",
        readonly=True,
        store=True,
        related="order_partner_id.country_id",
    )

    product_tmpl_model_id = fields.Many2one(
        "product.template",
        string="Shoes Model",
        store=True,
        related="product_id.product_tmpl_model_id",
    )
    color_attribute_id = fields.Many2one(
        "product.attribute.value",
        string="Shoes Color",
        store=True,
        related="product_id.color_attribute_id",
    )
    shoes_campaign_id = fields.Many2one(
        "project.project",
        string="Shoes Campaign",
        store=True,
        related="order_id.shoes_campaign_id",
    )
    product_brand_id = fields.Many2one(
        "product.brand",
        string="Brand",
        store=True,
        related="product_id.product_brand_id",
    )
    product_tmpl_id = fields.Many2one(
        string="S Model",
        comodel_name="product.template",
        related="product_id.product_tmpl_id",
        store=True,
        help="Used for group views in sale order line",
    )
    manufacturer_id = fields.Many2one(
        string="Manufacturer",
        comodel_name="res.partner",
        related="product_id.manufacturer_id",
        store=True,
        help="Used for group by manufacturer in sale order line views",
    )

    @api.depends("state")
    def _get_quoted_quantity(self):
        for record in self:
            total = 0
            if record.state not in ["sale", "done", "cancel"]:
                total = record.product_uom_qty
            record["qty_quoted"] = total

    qty_quoted = fields.Float(
        "Quoted qty", store=True, copy=False, compute="_get_quoted_quantity"
    )

    # ========= FIN INFORMES

    # Precio por par según tarifa:
    @api.depends("product_id", "price_unit")
    def _get_shoes_pair_price(self):
        for record in self:
            total = 0
            if record.pairs_count != 0:
                total = record.price_subtotal / record.pairs_count
            record["pair_price"] = total

    pair_price = fields.Float("Pair price", store=True, compute="_get_shoes_pair_price")

    product_saleko_id = fields.Many2one(
        "product.product", string="Product KO", store=True, copy=True
    )

    @api.onchange("product_saleko_id")
    def change_saleproductok_2_saleproductko(self):
        self.product_id = self.product_saleko_id.id


    @api.onchange('name')
    def _check_valid_shoes_assortment_custom_attributes(self):
        for record in self:
            #            cleanvalues, sizes, pairs, pair_products, pairs_count = "", "", "", "", 0
            size_attribute = self.env.company.size_attribute_id
            sale_line_product = record.product_id
            sale_line_product_color = sale_line_product.color_attribute_id
            shoes_pair_model = sale_line_product.product_tmpl_single_id

            # Si pongo en el if record.product_custom_attribute_value_ids, no pasa (uso name) !!
            if sale_line_product.is_assortment and record.name:
                try:
                    customvalue = record.product_custom_attribute_value_ids[0].custom_value
                except:
                    continue

                if customvalue:
                    # Quitar espacios del campo custom del surtido:
                    customvalue = customvalue.replace(" ", "").lower()
                    customvalues = customvalue.split(",")

                    # Chequear que las tallas o cantidades introducidas son válidas y el par está creado:
                    for li in customvalues:
                        element = li.split("x")
                        # Para tallas (encontrar si existe la talla y color en el par):
                        color_attribute_value_id = sale_line_product_color
                        size_attribute_value_id = self.env['product.attribute.value'].search(
                            [('attribute_id', '=', size_attribute.id), ('name', '=', element[0])])
                        if not size_attribute_value_id.id:
                            raise UserError("La talla " + str(element[0]) + " no existe en el sistema.")

                        pppair = self.env['product.product'].search([('color_attribute_id', '=', color_attribute_value_id.id),
                                                                     ('size_attribute_id', '=', size_attribute_value_id.id),
                                                                     ('product_tmpl_id', '=', shoes_pair_model.id)])
                        if not pppair.id:
                            raise UserError("No encuentro el par suelto de talla " + str(
                                element[0]) + " y color " + color_attribute_value_id.name + " en este modelo.")

                        # Para cantidades (ok):
                        try:
                            qty = int(element[1])
                        except:
                            raise UserError(element[1] + ", no parece una cantidad válida. Indica un número entero válido.")
"""
                        sizes += element[0] + ","
                        pairs += element[1] + ","
                        pair_products += str(pppair.id) + ","
                        pairs_count += int(element[1])

                    # OK, guardamos valores, tras quitar la última coma:
                    if len(sizes) > 0: sizes = sizes[:-1]
                    if len(pairs) > 0: pairs = pairs[:-1]
                    if len(pair_products) > 0: pair_products = pair_products[:-1]

                    cleanvalues = sizes + ";" + pairs + ";" + pair_products
                    record.write(
                        {'assortment_pair': cleanvalues, 'custom_assortment_pairs': pairs_count})
"""