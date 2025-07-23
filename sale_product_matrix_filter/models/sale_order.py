# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # Campo adicional para filtrar por múltiples atributos
    value_filter_ids = fields.Many2many(
        'product.attribute.value',
        'sale_order_attribute_value_rel',
        'sale_order_id',
        'attribute_value_id',
        string='Filtros de Variante',
        help="Filtrar productos de la matriz que contengan estos valores de atributo"
    )

    def _get_matrix(self, product_template):
        """Return the matrix of the given product, updated with current SOLines quantities.
        
        Modificado para filtrar productos basándose en value_filter_id si está establecido.

        :param product.template product_template:
        :return: matrix to display
        :rtype dict:
        """
        def has_ptavs(line, sorted_attr_ids):
            # TODO instead of sorting on ids, use odoo-defined order for matrix ?
            ptav = line.product_template_attribute_value_ids.ids
            pnav = line.product_no_variant_attribute_value_ids.ids
            pav = pnav + ptav
            pav.sort()
            return pav == sorted_attr_ids

        # Obtener la matriz base del template
        matrix = product_template._get_template_matrix(
            company_id=self.company_id,
            currency_id=self.currency_id,
            display_extra_price=True)
        
        # Si hay filtros de valores de atributo establecidos, filtrar la matriz
        if self.value_filter_ids:
            filter_names = self.value_filter_ids.mapped('name')
            filter_ids = set(self.value_filter_ids.ids)  # Usar set para búsqueda más eficiente
            
            # Primero, identificar qué columnas son válidas (tienen variantes filtradas)
            valid_column_indices = set()
            original_matrix = matrix['matrix']
            
            for row in original_matrix:
                if row:
                    for col_idx, cell in enumerate(row[1:], 1):  # Saltar header de fila
                        if cell.get('ptav_ids'):
                            cell_ptavs = self.env['product.template.attribute.value'].browse(cell['ptav_ids'])
                            cell_attribute_value_ids = cell_ptavs.mapped('product_attribute_value_id.id')
                            
                            # Si esta celda coincide con los filtros, marcar la columna como válida
                            if filter_ids.intersection(set(cell_attribute_value_ids)):
                                valid_column_indices.add(col_idx)
            
            if not valid_column_indices:
                # No hay variantes que coincidan con los filtros
                raise ValidationError(
                    _("No hay variantes disponibles que coincidan con los filtros seleccionados: %s.\n"
                      "Por favor, selecciona otros filtros o elimina los filtros actuales.") % ', '.join(filter_names)
                )
            
            # Filtrar el header para solo incluir columnas válidas
            original_header = matrix['header']
            filtered_header = [original_header[0]]  # Mantener primera columna (vacía)
            
            for col_idx in sorted(valid_column_indices):
                if col_idx < len(original_header):
                    filtered_header.append(original_header[col_idx])
            
            # Filtrar las filas para solo incluir columnas válidas
            filtered_matrix = []
            has_matching_variants = False
            
            for row in original_matrix:
                if row:
                    filtered_row = [row[0]]  # Mantener header de fila
                    
                    # Solo incluir celdas de columnas válidas
                    for col_idx in sorted(valid_column_indices):
                        if col_idx < len(row):
                            cell = row[col_idx]
                            if cell.get('ptav_ids'):
                                cell_ptavs = self.env['product.template.attribute.value'].browse(cell['ptav_ids'])
                                cell_attribute_value_ids = cell_ptavs.mapped('product_attribute_value_id.id')
                                
                                # Verificar si hay intersección entre los filtros y los valores de la celda
                                if filter_ids.intersection(set(cell_attribute_value_ids)):
                                    filtered_row.append(cell)
                                    has_matching_variants = True
                    
                    # Solo agregar la fila si tiene celdas además del header
                    if len(filtered_row) > 1:
                        filtered_matrix.append(filtered_row)
            
            # Actualizar la matriz con los datos filtrados
            matrix['header'] = filtered_header
            matrix['matrix'] = filtered_matrix
        
        # Aplicar cantidades de líneas de orden existentes
        if self.order_line and matrix.get('matrix'):
            lines = matrix['matrix']
            order_lines = self.order_line.filtered(lambda line: line.product_template_id == product_template)
            for line in lines:
                for cell in line:
                    if not cell.get('name', False) and cell.get('ptav_ids'):
                        matching_line = order_lines.filtered(lambda ol: has_ptavs(ol, cell['ptav_ids']))
                        if matching_line:
                            cell.update({
                                'qty': sum(matching_line.mapped('product_uom_qty'))
                            })
        
        return matrix

    @api.onchange('value_filter_ids')
    def _onchange_value_filter_ids(self):
        """Actualizar la matriz cuando cambien los filtros de atributos"""
        # Actualizar matriz si está disponible
        if hasattr(self, 'grid_product_tmpl_id') and self.grid_product_tmpl_id:
            # Trigger recalculation of matrix if a template is currently selected
            self._set_grid_up()

    @api.onchange('partner_id')
    def _onchange_partner_id_filter_values(self):
        """Establecer filtros por defecto basados en partner o company"""
        if self.partner_id:
            if self.partner_id.value_filter_ids:
                # Si el partner tiene filtros específicos, usarlos
                self.value_filter_ids = self.partner_id.value_filter_ids
            else:
                # Si el partner no tiene filtros, usar los de la company
                self.value_filter_ids = self.env.company.default_sale_filter_value_ids
        else:
            # Si no hay partner, usar los de la company
            self.value_filter_ids = self.env.company.default_sale_filter_value_ids

    @api.model
    def default_get(self, fields_list):
        """Establecer valores por defecto al crear un nuevo pedido"""
        defaults = super().default_get(fields_list)
        if 'value_filter_ids' in fields_list:
            # Solo establecer si no hay un valor específico ya establecido
            if not defaults.get('value_filter_ids'):
                defaults['value_filter_ids'] = [(6, 0, self.env.company.default_sale_filter_value_ids.ids)]
        return defaults
