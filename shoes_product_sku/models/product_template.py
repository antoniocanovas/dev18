# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shoes_sku_count = fields.Integer('SKU', compute='_compute_shoes_sku_count')
    # Computed for display on product.template form (first variant's SKU, usually unique per template+color)
    shoes_sku_id = fields.Many2one(
        'shoes.sku',
        string='SKU',
        compute='_compute_shoes_sku_id',
        store=False,
    )

    @api.depends('product_variant_ids.shoes_sku_id')
    def _compute_shoes_sku_count(self):
        for tmpl in self:
            tmpl.shoes_sku_count = len(
                tmpl.product_variant_ids.mapped('shoes_sku_id').filtered('id')
            )

    @api.depends('product_variant_ids.shoes_sku_id')
    def _compute_shoes_sku_id(self):
        for tmpl in self:
            skus = tmpl.product_variant_ids.mapped('shoes_sku_id').filtered('id')
            tmpl.shoes_sku_id = skus[:1]

    def action_view_shoes_sku(self):
        self.ensure_one()
        sku_ids = self.product_variant_ids.mapped('shoes_sku_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'SKU',
            'res_model': 'shoes.sku',
            'view_mode': 'list,form',
            'domain': [('id', 'in', sku_ids)],
            'context': {'create': False},
        }

    # Función para actualizar códigos de variantes para pares y surtidos en función de la configuración en la empresa:
    def _update_product_product_sku(self):
        for r in self:
            if not r.is_pair and not r.is_assortment:
                continue
            company = self.env.company
            config = company.shoes_sku_item_ids.ids

            id_campaign = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_campaign')]).res_id
            id_material = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_material')]).res_id
            id_manufacturer = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_manufacturer')]).res_id
            id_product = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_product_campaign_code')]).res_id
            id_color = self.env['ir.model.data'].sudo().search([('name', '=', 'sku_color')]).res_id

            skuconfig = self.env['shoes.product.sku.item'].search([('id', 'in', config)], order="sequence")

            code_campaign_type = company.shoes_code_campaign
            code_material_type = company.shoes_code_material
            code_manufacturer_type = company.shoes_code_manufacturer
            code_product_type = company.shoes_code_product
            code_color_type = company.shoes_code_color

            prefix_campaign = company.shoes_code_campaign_prefix or '' if code_campaign_type != 'none' else ''
            prefix_material = company.shoes_code_material_prefix or '' if code_material_type != 'none' else ''
            prefix_manufacturer = company.shoes_code_manufacturer_prefix or '' if code_manufacturer_type != 'none' else ''
            prefix_product = company.shoes_code_product_prefix or '' if code_product_type != 'none' else ''
            prefix_color = company.shoes_code_color_prefix or '' if code_color_type != 'none' else ''

            productprefix = r.shoes_task_id.shoes_default_code_prefix
            productsufix  = r.shoes_task_id.shoes_default_code_sufix

            for product in r.product_variant_ids:
                code_campaign, code_material, code_manufacturer, code_product, code_color = "", "", "", "", ""

                # Código de campaña:
                if code_campaign_type != 'none':
                    value = product.shoes_campaign_id.name if code_campaign_type == 'name' else product.shoes_campaign_id.task_code_prefix
                    if value:
                        code_campaign = prefix_campaign + value

                # Código de material:
                if code_material_type != 'none':
                    value = product.material_id.name if code_material_type == 'name' else product.material_id.code
                    if value:
                        code_material = prefix_material + value

                # Código de fabricante:
                if code_manufacturer_type != 'none':
                    value = product.manufacturer_id.name if code_manufacturer_type == 'name' else product.manufacturer_id.ref
                    if value:
                        code_manufacturer = prefix_manufacturer + value

                # Código de producto:
                if code_product_type != 'none':
                    value = product.name if code_product_type == 'name' else productprefix
                    if value:
                        code_product = prefix_product + value

                # Código de color:
                if code_color_type != 'none':
                    value = product.color_value_id.name if code_color_type == 'name' else product.color_value_id.code
                    if value:
                        code_color = prefix_color + value

                code_parts = {
                    id_campaign: code_campaign,
                    id_material: code_material,
                    id_manufacturer: code_manufacturer,
                    id_product: code_product,
                    id_color: code_color,
                }

                code = "".join([code_parts.get(item.id, '') for item in skuconfig])

                if productsufix:
                    code += productsufix

                product['default_code'] = code

        # Ensure SKU assignments are up to date
        for r in self:
            if r.is_pair or r.is_assortment:
                r.product_variant_ids._assign_shoes_sku()

        # Also process the related pair template for each assortment not already in self
        pair_templates = self.env['product.template']
        for r in self:
            if r.is_assortment and r.product_tmpl_single_id and r.product_tmpl_single_id not in self:
                pair_templates |= r.product_tmpl_single_id
        if pair_templates:
            pair_templates._update_product_product_sku()

    def create_shoe_pairs(self):
        self.ensure_one()
        res = super().create_shoe_pairs()
        if self.env.company.shoes_sku_update:
            self._update_product_product_sku()
            shoes_pair = self.product_tmpl_single_id
            shoes_pair._update_product_product_sku()
