# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    variant_selection_mode = fields.Selection([
        ('configurator', 'Product Configurator'),
        ('matrix', 'Order Grid Entry'),
        ('toggle', 'Allow Toggle')
    ], string='Variant Selection Mode', 
       default='configurator',
       help="Determina cómo se muestran las variantes en las líneas de venta:\n"
            "- Product Configurator: Ventana de configuración paso a paso\n"
            "- Order Grid Entry: Vista de matriz/cuadrícula\n"
            "- Allow Toggle: Permite elegir entre ambos formatos")
    
    def action_test_variant_toggle(self):
        """Acción para probar la configuración de toggle"""
        self.ensure_one()
        if self.variant_selection_mode != 'toggle':
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Selecciona "Allow Toggle" para probar esta funcionalidad',
                    'type': 'warning',
                }
            }
        
        # Abrir wizard de prueba
        return {
            'type': 'ir.actions.act_window',
            'name': f'Configurar: {self.name}',
            'res_model': 'variant.selector.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_product_template_id': self.id,
                'default_order_id': False,  # Sin orden específica
            }
        }
    
    def get_variant_selection_mode(self):
        """Método para obtener el modo de selección de variantes"""
        self.ensure_one()
        return self.variant_selection_mode
    
    def can_use_matrix_view(self):
        """Verifica si el producto puede usar vista de matriz"""
        self.ensure_one()
        return (
            len(self.attribute_line_ids) >= 1 and
            any(len(line.value_ids) >= 2 for line in self.attribute_line_ids)
        )
    
    def can_use_configurator_view(self):
        """Verifica si el producto puede usar vista de configurador"""
        self.ensure_one()
        return len(self.attribute_line_ids) >= 1
        
    def has_variants_to_configure(self):
        """Verifica si el producto tiene variantes configurables"""
        self.ensure_one()
        return bool(self.attribute_line_ids)
