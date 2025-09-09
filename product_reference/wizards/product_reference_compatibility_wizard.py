# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductReferenceCompatibilityWizard(models.TransientModel):
    _name = 'product.reference.compatibility.wizard'
    _description = 'Wizard para Gestión de Compatibilidades'
    
    reference_id = fields.Many2one(
        'product.reference',
        'Referencia',
        required=True,
        help='Referencia para la cual gestionar compatibilidades'
    )
    
    current_compatible_ids = fields.Many2many(
        'product.reference',
        'wizard_current_compatibility_rel',
        'wizard_id',
        'reference_id',
        string='Compatibles Actuales',
        help='Referencias actualmente compatibles (solo lectura)'
    )
    
    new_compatible_ids = fields.Many2many(
        'product.reference',
        'wizard_new_compatibility_rel',
        'wizard_id',
        'reference_id',
        string='Seleccionar Compatibles',
        help='Seleccionar las referencias que serán compatibles'
    )
    
    mode = fields.Selection([
        ('replace', 'Reemplazar todas las compatibilidades'),
        ('add', 'Añadir a las compatibilidades existentes'),
        ('remove', 'Eliminar compatibilidades seleccionadas')
    ], string='Modo de Operación', default='replace', required=True)
    
    @api.onchange('reference_id')
    def _onchange_reference_id(self):
        """Update current compatibles when reference changes"""
        if self.reference_id:
            # Get all current compatible references
            compatibles = self.reference_id.all_compatible_ids
            self.current_compatible_ids = compatibles
            
            # Set domain to exclude the reference itself
            return {
                'domain': {
                    'new_compatible_ids': [
                        ('id', '!=', self.reference_id.id),
                        ('active', '=', True)
                    ]
                }
            }
        else:
            self.current_compatible_ids = False
            return {'domain': {'new_compatible_ids': []}}
    
    @api.onchange('mode')
    def _onchange_mode(self):
        """Set default values based on mode"""
        if self.mode == 'replace':
            # Pre-select current compatibles for replacement mode
            self.new_compatible_ids = self.current_compatible_ids
        elif self.mode in ['add', 'remove']:
            # Clear selection for add/remove modes
            self.new_compatible_ids = False
    
    def action_update_compatibility(self):
        """Update compatibility relationships based on selected mode"""
        self.ensure_one()
        
        if not self.reference_id:
            raise ValidationError("Debe seleccionar una referencia.")
        
        compatibility_model = self.env['product.reference.compatibility']
        
        if self.mode == 'replace':
            self._replace_compatibilities()
        elif self.mode == 'add':
            self._add_compatibilities()
        elif self.mode == 'remove':
            self._remove_compatibilities()
        
        # Show success message
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Éxito',
                'message': f'Compatibilidades actualizadas para {self.reference_id.name}',
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _replace_compatibilities(self):
        """Replace all current compatibilities with selected ones"""
        compatibility_model = self.env['product.reference.compatibility']
        
        # Remove all existing compatibilities for this reference
        existing_compatibilities = compatibility_model.search([
            '|',
            ('reference_id', '=', self.reference_id.id),
            ('compatible_id', '=', self.reference_id.id)
        ])
        existing_compatibilities.unlink()
        
        # Create new compatibilities
        self._create_compatibilities(self.new_compatible_ids)
    
    def _add_compatibilities(self):
        """Add new compatibilities to existing ones"""
        if not self.new_compatible_ids:
            raise ValidationError("Debe seleccionar al menos una referencia para añadir.")
        
        # Filter out already existing compatibilities
        current_ids = self.current_compatible_ids.ids
        new_ids = [ref_id for ref_id in self.new_compatible_ids.ids if ref_id not in current_ids]
        
        if not new_ids:
            raise ValidationError("Todas las referencias seleccionadas ya son compatibles.")
        
        new_references = self.env['product.reference'].browse(new_ids)
        self._create_compatibilities(new_references)
    
    def _remove_compatibilities(self):
        """Remove selected compatibilities"""
        if not self.new_compatible_ids:
            raise ValidationError("Debe seleccionar al menos una referencia para eliminar.")
        
        compatibility_model = self.env['product.reference.compatibility']
        
        # Find and remove selected compatibilities
        for compatible in self.new_compatible_ids:
            compatibility_to_remove = compatibility_model.search([
                '|',
                '&', ('reference_id', '=', self.reference_id.id),
                     ('compatible_id', '=', compatible.id),
                '&', ('reference_id', '=', compatible.id),
                     ('compatible_id', '=', self.reference_id.id)
            ])
            compatibility_to_remove.unlink()
    
    def _create_compatibilities(self, compatible_references):
        """Create compatibility records for the given references"""
        compatibility_model = self.env['product.reference.compatibility']
        
        for compatible in compatible_references:
            # Check if compatibility already exists
            existing = compatibility_model.search([
                '|',
                '&', ('reference_id', '=', self.reference_id.id),
                     ('compatible_id', '=', compatible.id),
                '&', ('reference_id', '=', compatible.id),
                     ('compatible_id', '=', self.reference_id.id)
            ])
            
            if not existing:
                compatibility_model.create({
                    'reference_id': self.reference_id.id,
                    'compatible_id': compatible.id,
                })
    
    def action_preview_changes(self):
        """Preview the changes that will be made"""
        self.ensure_one()
        
        current_names = self.current_compatible_ids.mapped('name')
        new_names = self.new_compatible_ids.mapped('name')
        
        if self.mode == 'replace':
            added = set(new_names) - set(current_names)
            removed = set(current_names) - set(new_names)
            message_parts = []
            if added:
                message_parts.append(f"Añadir: {', '.join(added)}")
            if removed:
                message_parts.append(f"Eliminar: {', '.join(removed)}")
            message = '\n'.join(message_parts) if message_parts else "Sin cambios"
            
        elif self.mode == 'add':
            added = set(new_names) - set(current_names)
            message = f"Añadir: {', '.join(added)}" if added else "Sin cambios (ya son compatibles)"
            
        elif self.mode == 'remove':
            removed = set(new_names) & set(current_names)
            message = f"Eliminar: {', '.join(removed)}" if removed else "Sin cambios (no son compatibles)"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Vista Previa de Cambios',
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
