# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _update_product_product_sku(self):
        for r in self:
#            if not r.is_pair or not r.is_assortment:
#                continue

            config = env.company.shoes_sku_item_ids.ids

            id_campaign = self.env['ir.model.data'].search([('name', '=', 'sku_campaign')]).res_id
            id_material = self.env['ir.model.data'].search([('name', '=', 'sku_material')]).res_id
            id_manufacturer = self.env['ir.model.data'].search([('name', '=', 'sku_manufacturer')]).res_id
            id_product = self.env['ir.model.data'].search([('name', '=', 'sku_product_campaign_code')]).res_id
            id_color = self.env['ir.model.data'].search([('name', '=', 'sku_color')]).res_id

            skuconfig = self.env['shoes.product.sku.item'].search([('id', 'in', config)], order="sequence")

            for product in r.product_variant_ids:
                code = ""
                code_campaign = product.shoes_campaign_id.name if product.shoes_campaign_id.name else ""
                code_material = product.material_id.code if product.material_id.code else ""
                code_manufacturer = product.manufacturer_id.ref if product.manufacturer_id.ref else ""
                code_product = product.campaign_code if product.campaign_code else ""
                code_color = product.color_value_id.code if product.color_value_id.code else ""

                for item in skuconfig:
                    if item.id == id_campaign:       code += code_campaign
                    if item.id == id_material:       code += code_material
                    if item.id == id_manufacturer:   code += code_manufacturer
                    if item.id == id_product:        code += code_product
                    if item.id == id_color:          code += code_color
                product['default_code'] = code
            raise UserError('Hola')