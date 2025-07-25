# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    configurator_mode = fields.Selection([
        ('matrix', 'Matrix Grid'),
        ('configurator', 'Product Configurator')
    ], string="Configuration Mode", default='matrix',
       help="Choose how to configure this product:\n"
            "- Matrix Grid: Use the traditional matrix interface\n"
            "- Product Configurator: Use the step-by-step configurator dialog")

    @api.onchange('product_template_id')
    def _onchange_product_template_configurator_mode(self):
        """Auto-select mode based on product configuration"""
        if self.product_template_id and self.product_template_id.attribute_line_ids:
            # Set default mode based on product configuration
            if hasattr(self.product_template_id, 'product_add_mode'):
                if self.product_template_id.product_add_mode == 'matrix':
                    self.configurator_mode = 'matrix'
                else:
                    self.configurator_mode = 'configurator'
            else:
                # Fallback if product_add_mode doesn't exist
                self.configurator_mode = 'matrix'
        else:
            # No attributes, no need for special configuration
            self.configurator_mode = 'matrix'

    def action_open_product_configurator(self):
        """Open product configurator dialog"""
        self.ensure_one()
        
        if not self.product_template_id:
            raise UserError(_("Please select a product first."))
        
        if not self.product_template_id.attribute_line_ids:
            raise UserError(_("This product has no attributes to configure."))

        # Prepare context for the configurator
        return {
            'type': 'ir.actions.client',
            'tag': 'sale_product_configurator_dialog',
            'target': 'new',
            'context': {
                'default_product_template_id': self.product_template_id.id,
                'default_quantity': self.product_uom_qty or 1.0,
                'default_currency_id': self.order_id.currency_id.id,
                'default_pricelist_id': self.order_id.pricelist_id.id,
                'default_so_date': self.order_id.date_order.isoformat() if self.order_id.date_order else fields.Datetime.now().isoformat(),
                'default_company_id': self.order_id.company_id.id,
                'default_product_uom_id': self.product_uom.id if self.product_uom else False,
                'default_ptav_ids': self.product_template_attribute_value_ids.ids,
                'default_order_line_id': self.id,
                'configurator_mode': True,
            }
        }

    def _should_show_matrix(self):
        """Determine if matrix should be shown for this line"""
        # Only show matrix if:
        # 1. Mode is explicitly set to matrix
        # 2. Product has matrix configuration
        # 3. Product has attributes
        return (
            self.configurator_mode == 'matrix' and
            hasattr(self.product_template_id, 'product_add_mode') and
            self.product_template_id.product_add_mode == 'matrix' and
            self.product_template_id.attribute_line_ids
        )

    def _should_show_configurator_button(self):
        """Determine if configurator button should be shown"""
        return (
            self.configurator_mode == 'configurator' and
            self.product_template_id and
            self.product_template_id.attribute_line_ids
        )

    @api.constrains('configurator_mode', 'product_template_id')
    def _check_configurator_mode_compatibility(self):
        """Validate configurator mode compatibility"""
        for line in self:
            if line.configurator_mode == 'matrix' and line.product_template_id:
                # Check if product supports matrix mode
                if (hasattr(line.product_template_id, 'product_add_mode') and 
                    line.product_template_id.product_add_mode not in ['matrix', False]):
                    # Allow but could add warning in future versions
                    pass

    def write(self, vals):
        """Override write to handle configurator mode changes"""
        # If configurator_mode is being changed, we might need to reset some fields
        if 'configurator_mode' in vals:
            for line in self:
                if (line.configurator_mode != vals['configurator_mode'] and 
                    line.product_template_id and line.product_template_id.attribute_line_ids):
                    # Mode is changing for a configurable product
                    # Could add logic here to handle the transition
                    pass
        
        return super().write(vals)
