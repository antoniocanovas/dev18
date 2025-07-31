# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    configurator_mode = fields.Selection([
        ('matrix', 'Matrix Grid'),
        ('configurator', 'Product Configurator')
    ], string="Config Mode", default='matrix',
       help="Choose how to configure this product")

    configurator_mode_manual = fields.Boolean(
        default=False,
        help="Technical field to track manual mode selection"
    )

    @api.onchange('product_template_id')
    def _onchange_product_template_configurator_mode(self):
        """Auto-select mode based on product configuration only if not manually set"""
        if not self.configurator_mode_manual and self.product_template_id:
            if hasattr(self.product_template_id, 'product_add_mode'):
                self.configurator_mode = (
                    'matrix' if self.product_template_id.product_add_mode == 'matrix' 
                    else 'configurator'
                )

    @api.onchange('configurator_mode')
    def _onchange_configurator_mode(self):
        """Mark mode as manually selected when user changes it"""
        if self.configurator_mode:
            self.configurator_mode_manual = True

    @api.model_create_multi
    def create(self, vals_list):
        """Reset manual flag on creation"""
        for vals in vals_list:
            vals['configurator_mode_manual'] = False
        return super().create(vals_list)

    def copy(self, default=None):
        """Reset manual flag on copy"""
        if default is None:
            default = {}
        default['configurator_mode_manual'] = False
        return super().copy(default)


class ProductAttributeCustomValue(models.Model):
    _inherit = 'product.attribute.custom.value'
    
    # Add the field that is referenced by inverse_name in sale.order.line
    sale_order_line_id = fields.Many2one(
        'sale.order.line', 
        string="Sale Order Line", 
        ondelete='cascade'
    )
