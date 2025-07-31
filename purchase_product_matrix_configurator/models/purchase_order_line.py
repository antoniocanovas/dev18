# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    configurator_mode = fields.Selection([
        ('matrix', 'Matrix Grid'),
        ('configurator', 'Product Configurator (Matrix)')
    ], string="Config Mode", default='matrix',
       help="Choose how to configure this product. Note: Purchase orders always use Matrix Grid.")

    configurator_mode_manual = fields.Boolean(
        default=False,
        help="Technical field to track manual mode selection"
    )

    # Campo de valor variable
    variable_value = fields.Float(
        string="Variable Value",
        digits='Product Price',
        help="Variable value for this product line",
        default=0.0
    )

    # Campo alternativo para porcentaje variable
    variable_percentage = fields.Float(
        string="Variable %",
        digits=(16, 2),
        help="Variable percentage applied to this line",
        default=0.0
    )

    # Campo para costo variable del producto
    variable_cost = fields.Float(
        string="Variable Cost",
        digits='Product Price',
        help="Variable cost per unit for this product",
        default=0.0
    )

    # Total incluyendo valor variable
    price_total_with_variable = fields.Monetary(
        string="Total + Variable",
        compute='_compute_total_with_variable',
        store=True,
        help="Total price including variable value"
    )

    @api.depends('price_total', 'variable_value', 'product_qty')
    def _compute_total_with_variable(self):
        """Calculate total including variable value"""
        for line in self:
            line.price_total_with_variable = line.price_total + (line.variable_value * line.product_qty)

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
    
    # Add the field that is referenced by inverse_name in purchase.order.line
    purchase_order_line_id = fields.Many2one(
        'purchase.order.line', 
        string="Purchase Order Line", 
        ondelete='cascade'
    )
