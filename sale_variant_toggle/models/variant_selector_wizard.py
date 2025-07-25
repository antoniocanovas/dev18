# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class VariantSelectorWizard(models.TransientModel):
    _name = 'variant.selector.wizard'
    _description = 'Wizard para seleccionar formato de variantes'
    
    product_template_id = fields.Many2one(
        'product.template', 
        string='Product Template',
        required=True
    )
    product_name = fields.Char(
        related='product_template_id.name',
        string='Product Name'
    )
    order_id = fields.Many2one(
        'sale.order',
        string='Sale Order'
    )
    mode = fields.Selection([
        ('configurator', 'Configurador'),
        ('matrix', 'Matriz'),
    ], string='Modo Seleccionado')
    
    def action_use_configurator(self):
        """Acción para usar el configurador"""
        self.ensure_one()
        
        if self.order_id:
            # Llamar al método de la orden para abrir el configurador
            return self.order_id.action_open_variant_selector(
                self.product_template_id.id, 
                mode='configurator'
            )
        else:
            # Modo de prueba - solo mostrar notificación
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Configurador seleccionado para {self.product_name}',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    def action_use_matrix(self):
        """Acción para usar la matriz"""
        self.ensure_one()
        
        if self.order_id:
            # Llamar al método de la orden para abrir la matriz
            return self.order_id.action_open_variant_selector(
                self.product_template_id.id, 
                mode='matrix'
            )
        else:
            # Modo de prueba - solo mostrar notificación
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': f'Matriz seleccionada para {self.product_name}',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    @api.model
    def open_for_product(self, product_template_id, order_id=None):
        """Método para abrir el wizard desde JavaScript"""
        wizard = self.create({
            'product_template_id': product_template_id,
            'order_id': order_id,
        })
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Seleccionar Formato de Variantes',
            'res_model': 'variant.selector.wizard',
            'res_id': wizard.id,
            'view_mode': 'form',
            'target': 'new',
            'context': self.env.context,
        }
