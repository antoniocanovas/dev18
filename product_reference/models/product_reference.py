# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductReference(models.Model):
    _name = 'product.reference'
    _description = 'Referencia de Producto'
    _order = 'name'
    
    name = fields.Char(
        'Nombre de Referencia',
        required=True,
        help='Nombre único de la referencia del producto'
    )
    
    description = fields.Text(
        'Descripción',
        help='Descripción detallada de la referencia'
    )
    
    active = fields.Boolean(
        'Activo',
        default=True,
        help='Desmarcar para archivar la referencia'
    )
    
    compatibility_ids = fields.One2many(
        'product.reference.compatibility',
        'reference_id',
        string='Compatibilidades Directas',
        help='Compatibilidades donde esta referencia es el origen'
    )
    
    inverse_compatibility_ids = fields.One2many(
        'product.reference.compatibility',
        'compatible_id',
        string='Compatibilidades Inversas',
        help='Compatibilidades donde esta referencia es el destino'
    )
    
    all_compatible_ids = fields.Many2many(
        'product.reference',
        compute='_compute_all_compatible_ids',
        string='Todas las Referencias Compatibles',
        help='Todas las referencias compatibles (directas e inversas)'
    )
    
    compatible_count = fields.Integer(
        'Número de Compatibilidades',
        compute='_compute_compatible_count',
        help='Contador de referencias compatibles'
    )
    
    @api.depends('compatibility_ids', 'inverse_compatibility_ids')
    def _compute_all_compatible_ids(self):
        """Compute all compatible references (both direct and inverse)"""
        for record in self:
            direct_compatibles = record.compatibility_ids.mapped('compatible_id')
            inverse_compatibles = record.inverse_compatibility_ids.mapped('reference_id')
            record.all_compatible_ids = direct_compatibles | inverse_compatibles
    
    @api.depends('all_compatible_ids')
    def _compute_compatible_count(self):
        """Compute the number of compatible references"""
        for record in self:
            record.compatible_count = len(record.all_compatible_ids)
    
    def action_manage_compatibility(self):
        """Open wizard to manage compatibilities"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Gestionar Compatibilidades',
            'res_model': 'product.reference.compatibility.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_reference_id': self.id,
                'default_current_compatible_ids': [(6, 0, self.all_compatible_ids.ids)]
            }
        }
    
    def action_view_compatibilities(self):
        """View all compatibility records for this reference"""
        return {
            'type': 'ir.actions.act_window',
            'name': f'Compatibilidades de {self.name}',
            'res_model': 'product.reference.compatibility',
            'view_mode': 'tree,form',
            'domain': [
                '|',
                ('reference_id', '=', self.id),
                ('compatible_id', '=', self.id)
            ],
            'context': {'default_reference_id': self.id}
        }
    
    _sql_constraints = [
        ('name_unique', 'UNIQUE(name)', 'El nombre de la referencia debe ser único.'),
    ]
