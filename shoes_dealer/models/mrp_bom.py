# Copyright Serincloud SL - Ingenieriacloud.com


from odoo import fields, models, api

class MrpBom(models.Model):
    _inherit = "mrp.bom"

    pairs_count = fields.Integer('Pairs', store=True, compute='_get_shoes_bom_pair_count')

    set_pairs_count = fields.Integer('Set pairs',
                                     related='product_id.assortment_attribute_id.assortment_id.pairs_count')

    is_assortment = fields.Boolean(related='product_tmpl_id.is_assortment')

    assortment_pair = fields.Char('Assortment pair', compute='_get_assortment_pair')


    # Pares por variante de producto, se usará en el cálculo de tarifas y líneas de venta:
    @api.depends('bom_line_ids','bom_line_ids.product_qty')
    def _get_shoes_bom_pair_count(self):
        for record in self:
            record.pairs_count = sum(li.product_qty for li in record.bom_line_ids) or 1

    @api.depends('bom_line_ids.product_qty')
    def _get_assortment_pair(self):
        for record in self:
            cleanvalues, sizes, pairs, pair_products = "", "", "", ""
            if record.product_id.is_assortment:
                for li in record.bom_line_ids:
                    if li.product_id.is_pair:
                        sizes += li.product_id.size_value_id.name + ","
                        pairs += str(int(li.product_qty)) + ","
                        pair_products += str(li.product_id.id) + ","
                if len(sizes) > 0: sizes = sizes[:-1]
                if len(pairs) > 0: pairs = pairs[:-1]
                if len(pair_products) > 0: pair_products = pair_products[:-1]

                cleanvalues = sizes + ";" + pairs + ";" + pair_products
            record['assortment_pair'] = cleanvalues

