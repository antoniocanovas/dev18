# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models
from odoo.exceptions import UserError


class ShoesSku(models.Model):
    _name = 'shoes.sku'
    _description = 'Shoes SKU'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char('SKU', required=True, tracking=True, copy=False, index=True)
    shoes_task_id = fields.Many2one(
        'project.task', string='Model', ondelete='restrict', tracking=True, index=True
    )
    shoes_campaign_id = fields.Many2one(
        'project.project',
        string='Campaign',
        related='shoes_task_id.project_id',
        store=True,
        index=True,
    )
    color_value_id = fields.Many2one(
        'product.attribute.value', string='Color', tracking=True, ondelete='restrict'
    )
    product_ids = fields.One2many(
        'product.product', 'shoes_sku_id', string='Variants'
    )
    product_count = fields.Integer('Variants', compute='_compute_product_count')
    product_tmpl_set_id = fields.Many2one(
        'product.template',
        string='Assortment',
        compute='_compute_tmpl_ids',
    )
    product_tmpl_single_id = fields.Many2one(
        'product.template',
        string='Pair',
        compute='_compute_tmpl_ids',
    )
    image = fields.Image('Image', max_width=1920, max_height=1920)
    image_1024 = fields.Image('Image 1024', related='image', max_width=1024, max_height=1024, store=True)
    image_512 = fields.Image('Image 512', related='image', max_width=512, max_height=512, store=True)
    image_256 = fields.Image('Image 256', related='image', max_width=256, max_height=256, store=True)
    image_128 = fields.Image('Image 128', related='image', max_width=128, max_height=128, store=True)
    product_image_ids = fields.One2many(
        'product.image', 'shoes_sku_id', string='Images'
    )
    shoes_sample_ids = fields.One2many(
        'shoes.sample', 'shoes_sku_id', string='Samples'
    )
    shoes_sample_count = fields.Integer('Samples', compute='_compute_shoes_sample_count')

    @api.depends('shoes_sample_ids')
    def _compute_shoes_sample_count(self):
        for sku in self:
            sku.shoes_sample_count = len(sku.shoes_sample_ids)

    @api.depends('product_ids')
    def _compute_product_count(self):
        for sku in self:
            sku.product_count = len(sku.product_ids)

    @api.depends(
        'product_ids.product_tmpl_id',
        'product_ids.product_tmpl_id.is_assortment',
        'product_ids.product_tmpl_id.is_pair',
    )
    def _compute_tmpl_ids(self):
        for sku in self:
            assortment_tmpls = sku.product_ids.filtered(
                lambda p: p.is_assortment
            ).mapped('product_tmpl_id')
            pair_tmpls = sku.product_ids.filtered(
                lambda p: p.is_pair
            ).mapped('product_tmpl_id')
            sku.product_tmpl_set_id = assortment_tmpls[:1]
            sku.product_tmpl_single_id = pair_tmpls[:1]

    def write(self, vals):
        result = super().write(vals)
        if 'image' in vals:
            for sku in self:
                templates = sku.product_ids.mapped('product_tmpl_id')
                if templates:
                    templates.with_context(_sku_image_sync=True).write({'image_1920': sku.image})
        return result

    def unlink(self):
        for sku in self:
            if sku.product_ids:
                raise UserError(
                    "No se puede eliminar un SKU con variantes de producto asociadas."
                )
        return super().unlink()

    def action_view_referrers(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Referrers Stock',
            'res_model': 'shoes.sample',
            'view_mode': 'list,form',
            'domain': [('shoes_sku_id', '=', self.id)],
            'context': {'default_shoes_sku_id': self.id, 'default_shoes_campaign_id': self.shoes_campaign_id.id},
        }

    def action_view_products(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Variants',
            'res_model': 'product.product',
            'view_mode': 'list,form',
            'domain': [('shoes_sku_id', '=', self.id)],
            'context': {'create': False},
        }

    def action_import_images(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Import Images / Videos',
            'res_model': 'shoes.sku.direct.import',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_shoes_sku_id': self.id},
        }
