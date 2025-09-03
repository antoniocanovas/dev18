from odoo import models, fields, api


class ProductSearchResult(models.Model):
    _name = 'product.search.result'
    _description = 'Resultado de Búsqueda de Productos'
    _order = 'relevance_score desc, id desc'

    search_id = fields.Many2one(
        'product.search',
        string='Búsqueda',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.template',
        string='Producto',
        required=True
    )
    
    # Campos relacionados del producto para mostrar en la vista
    product_name = fields.Char(
        related='product_id.name',
        string='Nombre del Producto',
        store=True
    )
    product_code = fields.Char(
        related='product_id.default_code',
        string='Código',
        store=True
    )
    product_price = fields.Float(
        related='product_id.list_price',
        string='Precio de Lista',
        store=True
    )
    product_category = fields.Char(
        related='product_id.categ_id.name',
        string='Categoría',
        store=True
    )
    product_image = fields.Image(
        related='product_id.image_128',
        string='Imagen'
    )
    product_active = fields.Boolean(
        related='product_id.active',
        string='Activo'
    )
    
    # Campos de análisis
    relevance_score = fields.Float(
        string='Puntuación de Relevancia',
        digits=(3, 1),
        help='Puntuación calculada basada en la relevancia del producto con la consulta'
    )
    
    # Campos computados
    relevance_level = fields.Selection([
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('perfect', 'Perfecta')
    ], string='Nivel de Relevancia', compute='_compute_relevance_level', store=True)
    
    match_details = fields.Text(
        string='Detalles de Coincidencia',
        compute='_compute_match_details'
    )

    @api.depends('relevance_score')
    def _compute_relevance_level(self):
        for record in self:
            score = record.relevance_score
            if score >= 80:
                record.relevance_level = 'perfect'
            elif score >= 50:
                record.relevance_level = 'high'
            elif score >= 20:
                record.relevance_level = 'medium'
            else:
                record.relevance_level = 'low'

    @api.depends('search_id', 'product_id')
    def _compute_match_details(self):
        for record in self:
            if not record.search_id or not record.product_id:
                record.match_details = ''
                continue
                
            details = []
            query = record.search_id.query_text.lower()
            product_name = record.product_id.name.lower()
            
            # Verificar coincidencias de marca
            if record.search_id.detected_brand:
                brand_lower = record.search_id.detected_brand.lower()
                if brand_lower in product_name:
                    details.append(f"✓ Marca: {record.search_id.detected_brand}")
                    
            # Verificar coincidencias de categoría
            if record.search_id.detected_category and record.product_id.categ_id:
                category_lower = record.search_id.detected_category.lower()
                product_category_lower = record.product_id.categ_id.name.lower()
                if category_lower in product_category_lower:
                    details.append(f"✓ Categoría: {record.product_id.categ_id.name}")
                    
            # Verificar palabras clave
            query_words = query.split()
            matched_words = []
            for word in query_words:
                if len(word) > 2 and word in product_name:
                    matched_words.append(word.title())
                    
            if matched_words:
                details.append(f"✓ Palabras clave: {', '.join(matched_words)}")
                
            record.match_details = '\n'.join(details) if details else 'Sin coincidencias específicas'

    def action_open_product(self):
        """Abrir vista del producto"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.template',
            'res_id': self.product_id.id,
            'view_mode': 'form',
            'target': 'new',
            'context': dict(self.env.context)
        }

    def action_add_to_sale_order(self):
        """Agregar producto a una orden de venta (funcionalidad futura)"""
        self.ensure_one()
        # Aquí se puede implementar lógica para agregar a cotización
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Producto seleccionado',
                'message': f'El producto "{self.product_name}" ha sido seleccionado',
                'type': 'success',
            }
        }
