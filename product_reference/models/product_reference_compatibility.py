# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ProductReferenceCompatibility(models.Model):
    _name = 'product.reference.compatibility'
    _description = 'Compatibilidad entre Referencias de Producto'
    _order = 'reference_id, compatible_id'
    _rec_name = 'display_name'
    
    reference_id = fields.Many2one(
        'product.reference',
        'Referencia Principal',
        required=True,
        ondelete='cascade',
        help='Referencia principal de la compatibilidad'
    )
    
    compatible_id = fields.Many2one(
        'product.reference',
        'Referencia Compatible',
        required=True,
        ondelete='cascade',
        help='Referencia compatible con la principal'
    )
    
    display_name = fields.Char(
        'Nombre',
        compute='_compute_display_name',
        store=True,
        help='Nombre de visualización de la compatibilidad'
    )
    
    active = fields.Boolean(
        'Activo',
        default=True,
        help='Desmarcar para desactivar la compatibilidad'
    )
    
    notes = fields.Text(
        'Notas',
        help='Notas adicionales sobre la compatibilidad'
    )
    
    @api.depends('reference_id.name', 'compatible_id.name')
    def _compute_display_name(self):
        """Compute display name for compatibility record"""
        for record in self:
            if record.reference_id and record.compatible_id:
                record.display_name = f"{record.reference_id.name} ↔ {record.compatible_id.name}"
            else:
                record.display_name = "Nueva Compatibilidad"
    
    @api.constrains('reference_id', 'compatible_id')
    def _check_no_self_compatibility(self):
        """Prevent a reference from being compatible with itself"""
        for record in self:
            if record.reference_id == record.compatible_id:
                raise ValidationError(
                    "Una referencia no puede ser compatible consigo misma."
                )
    
    @api.constrains('reference_id', 'compatible_id')
    def _check_unique_compatibility(self):
        """Ensure compatibility is unique (considering both directions)"""
        for record in self:
            if record.reference_id and record.compatible_id:
                # Check for existing compatibility in both directions
                existing = self.search([
                    ('id', '!=', record.id),
                    '|',
                    '&', ('reference_id', '=', record.reference_id.id),
                         ('compatible_id', '=', record.compatible_id.id),
                    '&', ('reference_id', '=', record.compatible_id.id),
                         ('compatible_id', '=', record.reference_id.id)
                ])
                if existing:
                    raise ValidationError(
                        f"Ya existe una compatibilidad entre "
                        f"{record.reference_id.name} y {record.compatible_id.name}."
                    )
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to ensure symmetric relationships"""
        records = super().create(vals_list)
        
        # Create symmetric relationships
        symmetric_vals = []
        for record in records:
            # Check if symmetric relationship already exists
            symmetric_exists = self.search([
                ('reference_id', '=', record.compatible_id.id),
                ('compatible_id', '=', record.reference_id.id)
            ])
            
            if not symmetric_exists:
                symmetric_vals.append({
                    'reference_id': record.compatible_id.id,
                    'compatible_id': record.reference_id.id,
                    'notes': record.notes,
                    'active': record.active,
                })
        
        if symmetric_vals:
            # Create symmetric relationships without triggering this method again
            super(ProductReferenceCompatibility, self).create(symmetric_vals)
        
        return records
    
    def unlink(self):
        """Override unlink to remove symmetric relationships"""
        symmetric_records = self.env['product.reference.compatibility']
        
        for record in self:
            # Find symmetric record
            symmetric = self.search([
                ('reference_id', '=', record.compatible_id.id),
                ('compatible_id', '=', record.reference_id.id)
            ])
            symmetric_records |= symmetric
        
        # Remove symmetric records first to avoid recursion
        if symmetric_records:
            super(ProductReferenceCompatibility, symmetric_records).unlink()
        
        return super().unlink()
    
    _sql_constraints = [
        ('unique_compatibility_pair', 
         'UNIQUE(reference_id, compatible_id)',
         'Esta combinación de compatibilidad ya existe.'),
    ]
