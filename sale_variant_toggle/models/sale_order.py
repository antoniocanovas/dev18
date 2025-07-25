# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    def action_open_variant_selector(self, product_template_id, mode='auto'):
        """Abre el selector de variantes según el modo especificado"""
        product_template = self.env['product.template'].browse(product_template_id)
        
        if mode == 'auto':
            mode = product_template.variant_selection_mode
            
        # Intentar abrir el configurador real según el modo
        if mode == 'matrix':
            return self._open_matrix_configurator(product_template)
        elif mode == 'configurator':
            return self._open_product_configurator(product_template)
        else:
            # Fallback al wizard
            return self._open_variant_selector_wizard(product_template)
    
    def _open_matrix_configurator(self, product_template):
        """Abre el configurador de matriz nativo de Odoo"""
        try:
            # Retornar acción para abrir configurador de matriz
            return {
                'type': 'ir.actions.act_window',
                'name': f'Configure: {product_template.name}',
                'res_model': 'sale.order.line',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'default_order_id': self.id,
                    'default_product_template_id': product_template.id,
                    'default_product_uom_qty': 1,
                    'sale_product_configurator': True,
                    'show_sale': True,
                    'force_matrix': True,
                }
            }
        except Exception:
            return self._open_product_configurator(product_template)
    
    def _open_product_configurator(self, product_template):
        """Abre el configurador de producto estándar"""
        try:
            # Obtener la primera variante para el configurador
            if product_template.product_variant_ids:
                variant = product_template.product_variant_ids[0]
                
                # Crear línea de pedido con el configurador
                return {
                    'type': 'ir.actions.act_window',
                    'name': f'Configure: {product_template.name}',
                    'res_model': 'sale.order.line',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {
                        'default_order_id': self.id,
                        'default_product_id': variant.id,
                        'default_product_template_id': product_template.id,
                        'default_product_uom_qty': 1,
                        'sale_product_configurator': True,
                        'show_sale': True,
                    }
                }
        except Exception:
            pass
        
        # Fallback al wizard
        return self._open_variant_selector_wizard(product_template)
    
    def _open_variant_selector_wizard(self, product_template):
        """Abre el wizard de selección como fallback"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Seleccionar Formato de Variantes',
            'res_model': 'variant.selector.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_template_id': product_template.id,
                'default_order_id': self.id,
            }
        }
    
    @api.model
    def check_variant_toggle_mode(self, product_template_id):
        """Método para verificar si un producto tiene modo toggle"""
        product = self.env['product.template'].browse(product_template_id)
        return {
            'variant_selection_mode': product.variant_selection_mode,
            'has_attributes': bool(product.attribute_line_ids),
            'name': product.name,
        }


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    # REMOVER el onchange que causa problemas
    # @api.onchange('product_template_id')
    # def _onchange_product_template_id_toggle(self):
    #     # Este onchange interfiere con el JavaScript
    #     pass
    
    def action_configure_variant(self):
        """Acción para configurar variantes desde la línea"""
        self.ensure_one()
        if not self.product_template_id:
            return False
            
        return self.order_id.action_open_variant_selector(
            self.product_template_id.id, 
            mode='auto'
        )
