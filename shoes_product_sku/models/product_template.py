# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProductTemplate(models.Model):
    _inherit = "product.template"

    # Función para actualizar códigos de variantes para pares y surtidos en función de la configuración en la empresa:
    def _update_product_product_sku(self):
        for r in self:
            if not r.is_pair and not r.is_assortment:
                continue
            config = self.env.company.shoes_sku_item_ids.ids

            id_campaign = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_campaign')]).res_id
            id_material = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_material')]).res_id
            id_manufacturer = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_manufacturer')]).res_id
            id_product = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_product_campaign_code')]).res_id
            id_color = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_color')]).res_id

            skuconfig = self.env['shoes.product.sku.item'].search([('id', 'in', config)], order="sequence")

            code_campaign_type = self.env.company.shoes_code_campaign
            code_material_type = self.env.company.shoes_code_material
            code_manufacturer_type = self.env.company.shoes_code_manufacturer
            code_product_type = self.env.company.shoes_code_product
            code_color_type = self.env.company.shoes_code_color

            productprefix = r.shoes_task_id.shoes_default_code_prefix
            productsufix  = r.shoes_task_id.shoes_default_code_sufix

            for product in r.product_variant_ids:
                code = ""

                # Código de campaña:
                if code_campaign_type == 'name' and product.shoes_campaign_id.name:
                    code_campaign = product.shoes_campaign_id.name
                elif code_campaign_type == 'code' and product.shoes_campaign_id.task_code_prefix:
                    code_campaign = product.shoes_campaign_id.task_code_prefix
                else:
                    code_campaign = ""

                # Código de material:
                if code_material_type == 'name' and product.material_id.name:
                    code_material = product.material_id.name
                elif code_material_type == 'code' and product.material_id.code:
                    code_material = product.material_id.code
                else:
                    code_material = ""

                # Código de fabricante:
                if code_manufacturer_type == 'name' and product.manufacturer_id.name:
                    code_manufacturer = product.manufacturer_id.name
                elif code_manufacturer_type == 'code' and product.manufacturer_id.ref:
                    code_manufacturer = product.manufacturer_id.ref
                else:
                    code_manufacturer = ""

                # Código de producto:
                if code_product_type == 'name' and product.name:
                    code_product = product.name
                elif code_product_type == 'code' and productprefix:
                    code_product = productprefix
                else:
                    code_product = ""

                # Código de color:
                if code_color_type == 'name' and product.color_value_id.name:
                    code_color = "-" + product.color_value_id.name + "-"
                elif code_color_type == 'code' and product.color_value_id.code:
                    code_color = "-" + product.color_value_id.code + "-"
                else:
                    code_color = ""


                for item in skuconfig:
                    if item.id == id_campaign:       code += code_campaign
                    if item.id == id_material:       code += code_material
                    if item.id == id_manufacturer:   code += code_manufacturer
                    if item.id == id_product:        code += code_product
                    if item.id == id_color:          code += code_color
                
                if productsufix:
                    code += productsufix

                product['default_code'] = code

    def create_shoe_pairs(self):
        self.ensure_one()
        res = super().create_shoe_pairs()
        if self.env.company.shoes_sku_update:
            self._update_product_product_sku()
            shoes_pair = self.product_tmpl_single_id
            shoes_pair._update_product_product_sku()
