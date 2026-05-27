# Copyright 2024 Ingenieriacloud.com

from odoo import api, fields, models


class ShoesSample(models.Model):
    _name = 'shoes.sample'
    _description = 'Shoes Sample'
    _order = 'shoes_campaign_id, name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(
        'Reference', required=True, copy=False, default='New',
        readonly=True, index=True,
    )
    partner_id = fields.Many2one(
        'res.partner', string='Referrer', required=True, tracking=True, index=True,
    )
    shoes_campaign_id = fields.Many2one(
        'project.project', string='Campaign',
        domain=[('is_shoes_campaign', '=', True)],
        required=True, tracking=True, index=True,
    )
    shoes_sku_id = fields.Many2one(
        'shoes.sku', string='SKU', required=True, tracking=True,
        domain="[('shoes_campaign_id', '=', shoes_campaign_id)]",
    )
    product_tmpl_set_id = fields.Many2one(
        'product.template', string='Assortment',
        related='shoes_sku_id.product_tmpl_set_id',
    )
    product_tmpl_single_id = fields.Many2one(
        'product.template', string='Pair',
        related='shoes_sku_id.product_tmpl_single_id',
    )
    shoes_task_id = fields.Many2one(
        'project.task', string='Model',
        related='shoes_sku_id.shoes_task_id', store=True, index=True,
    )
    product_brand_id = fields.Many2one(
        'product.brand', string='Brand',
        related='shoes_campaign_id.product_brand_id', store=True, index=True,
    )
    type = fields.Char(string='Type', size=2, required=True)
    date = fields.Date(string='Sent date', tracking=True, help='Sent date')
    image = fields.Image(related='shoes_sku_id.image')
    product_image_ids = fields.Many2many(
        'product.image', string='Images',
        compute='_compute_product_images',
    )
    product_image_html = fields.Html(
        'Images Preview', compute='_compute_product_image_html', sanitize=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('shoes.sample') or 'New'
        return super().create(vals_list)

    @api.depends('shoes_sku_id', 'shoes_sku_id.product_image_ids')
    def _compute_product_images(self):
        for rec in self:
            rec.product_image_ids = rec.shoes_sku_id.product_image_ids

    @api.depends('shoes_sku_id', 'shoes_sku_id.product_image_ids')
    def _compute_product_image_html(self):
        for rec in self:
            parts = [
                f'<img src="/web/image/product.image/{img.id}/image_128" '
                f'style="max-width:128px;max-height:128px;margin:2px;object-fit:contain;" alt=""/>'
                for img in rec.shoes_sku_id.product_image_ids
            ]
            rec.product_image_html = ''.join(parts) if parts else False

    def action_open_form(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'shoes.sample',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }
