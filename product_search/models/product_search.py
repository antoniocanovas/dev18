from odoo import models, fields, api
import re


class ProductSearch(models.Model):
    _name = 'product.search'
    _description = 'Búsqueda de Productos'
    _order = 'create_date desc'

    name = fields.Char(
        string='Nombre de Búsqueda', 
        compute='_compute_name',
        store=True
    )
    query_text = fields.Text(
        string='Texto de Consulta', 
        required=True,
        placeholder="Ej: Laptop HP para gaming, Teléfono Samsung económico..."
    )
    detected_brand = fields.Char(
        string='Marca Detectada',
        readonly=True
    )
    detected_category = fields.Char(
        string='Categoría Detectada', 
        readonly=True
    )
    search_performed = fields.Boolean(
        string='Búsqueda Realizada',
        default=False,
        readonly=True
    )
    result_count = fields.Integer(
        string='Productos Encontrados',
        compute='_compute_result_count',
        store=True
    )
    result_ids = fields.One2many(
        'product.search.result',
        'search_id',
        string='Resultados'
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('searching', 'Buscando...'),
        ('waiting_interaction', 'Esperando Respuestas'),
        ('done', 'Completado'),
        ('no_results', 'Sin Resultados')
    ], default='draft', string='Estado')
    
    # Campos del sistema conversacional
    interaction_ids = fields.One2many(
        'product.search.interaction',
        'search_id',
        string='Interacciones'
    )
    needs_interaction = fields.Boolean(
        string='Necesita Interacción',
        default=False,
        help='Indica si la búsqueda requiere más información del usuario'
    )
    interaction_completed = fields.Boolean(
        string='Interacción Completada',
        default=False
    )
    learning_data = fields.Text(
        string='Datos de Aprendizaje',
        help='Información aprendida para mejorar futuras búsquedas'
    )

    @api.depends('query_text')
    def _compute_name(self):
        for record in self:
            if record.query_text:
                # Tomar primeras 50 caracteres como nombre
                record.name = record.query_text[:50] + ('...' if len(record.query_text) > 50 else '')
            else:
                record.name = 'Nueva Búsqueda'

    @api.depends('result_ids')
    def _compute_result_count(self):
        for record in self:
            record.result_count = len(record.result_ids)

    def action_search_products(self):
        """Ejecutar búsqueda de productos"""
        self.ensure_one()
        
        if not self.query_text:
            return
            
        self.state = 'searching'
        
        # Detectar marca y categoría
        self._detect_brand_and_category()
        self._apply_learned_patterns()
        
        # Limpiar resultados anteriores
        self.result_ids.unlink()
        
        # Buscar productos
        products = self._search_products()
        
        # Crear resultados
        self._create_search_results(products)
        
        # Evaluar si necesita interacción del usuario
        needs_questions = self._evaluate_search_quality()
        
        if needs_questions:
            self.needs_interaction = True
            self.state = 'waiting_interaction'
            # Generar preguntas inteligentes
            question_count = self.env['product.search.interaction'].generate_questions_for_search(self.id)
            return self._show_interaction_wizard()
        else:
            self.state = 'done' if self.result_count > 0 else 'no_results'
            
        self.search_performed = True
        return True

    def _detect_brand_and_category(self):
        """Detectar marca y categoría del texto"""
        text = self.query_text.lower()
        
        # Diccionario de marcas comunes
        brands = {
            'hp': 'HP',
            'hewlett packard': 'HP',
            'dell': 'Dell',
            'lenovo': 'Lenovo',
            'apple': 'Apple',
            'samsung': 'Samsung',
            'sony': 'Sony',
            'lg': 'LG',
            'asus': 'ASUS',
            'acer': 'Acer',
            'huawei': 'Huawei',
            'xiaomi': 'Xiaomi',
            'canon': 'Canon',
            'epson': 'Epson',
            'nike': 'Nike',
            'adidas': 'Adidas'
        }
        
        # Diccionario de categorías
        categories = {
            'laptop': 'Laptop',
            'computadora': 'Computadora',
            'pc': 'Computadora',
            'telefono': 'Teléfono',
            'celular': 'Teléfono',
            'smartphone': 'Smartphone',
            'tablet': 'Tablet',
            'monitor': 'Monitor',
            'pantalla': 'Monitor',
            'teclado': 'Teclado',
            'mouse': 'Mouse',
            'ratón': 'Mouse',
            'impresora': 'Impresora',
            'camara': 'Cámara',
            'audifonos': 'Audífonos',
            'auriculares': 'Audífonos',
            'gaming': 'Gaming',
            'gamer': 'Gaming',
            'office': 'Oficina',
            'oficina': 'Oficina'
        }
        
        # Detectar marca
        detected_brand = None
        for brand_key, brand_value in brands.items():
            if brand_key in text:
                detected_brand = brand_value
                break
                
        # Detectar categoría
        detected_category = None
        for category_key, category_value in categories.items():
            if category_key in text:
                detected_category = category_value
                break
                
        self.detected_brand = detected_brand
        self.detected_category = detected_category

    def _search_products(self):
        """Buscar productos basado en el texto y detecciones"""
        domain = []
        
        # Buscar por marca detectada
        if self.detected_brand:
            domain.append('|')
            domain.append(('name', 'ilike', self.detected_brand))
            domain.append(('default_code', 'ilike', self.detected_brand))
            
        # Buscar por categoría detectada
        if self.detected_category:
            if domain:
                domain.insert(0, '&')
            domain.append('|')
            domain.append(('categ_id.name', 'ilike', self.detected_category))
            domain.append(('name', 'ilike', self.detected_category))
            
        # Si no se detectó nada específico, buscar por palabras clave
        if not self.detected_brand and not self.detected_category:
            words = self.query_text.split()
            # Filtrar palabras muy comunes
            stop_words = ['el', 'la', 'de', 'para', 'con', 'un', 'una', 'que', 'es', 'en', 'y', 'a']
            keywords = [word for word in words if len(word) > 2 and word.lower() not in stop_words]
            
            if keywords:
                domain = ['|'] * (len(keywords) - 1)
                for keyword in keywords:
                    domain.append(('name', 'ilike', keyword))
        
        # Si no hay dominio, buscar todos los productos activos
        if not domain:
            domain = [('active', '=', True)]
            
        # Limitar resultados
        products = self.env['product.template'].search(domain, limit=20)
        
        return products

    def _create_search_results(self, products):
        """Crear registros de resultados de búsqueda"""
        results_data = []
        
        for product in products:
            # Calcular relevancia basada en coincidencias
            relevance_score = self._calculate_relevance(product)
            
            results_data.append({
                'search_id': self.id,
                'product_id': product.id,
                'relevance_score': relevance_score,
            })
            
        # Ordenar por relevancia
        results_data.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Crear registros
        for data in results_data:
            self.env['product.search.result'].create(data)

    def _calculate_relevance(self, product):
        """Calcular puntaje de relevancia del producto"""
        score = 0
        query_lower = self.query_text.lower()
        product_name_lower = product.name.lower()
        
        # Coincidencia exacta de marca
        if self.detected_brand and self.detected_brand.lower() in product_name_lower:
            score += 50
            
        # Coincidencia de categoría
        if self.detected_category:
            if product.categ_id and self.detected_category.lower() in product.categ_id.name.lower():
                score += 30
            elif self.detected_category.lower() in product_name_lower:
                score += 20
                
        # Coincidencias de palabras clave
        query_words = query_lower.split()
        for word in query_words:
            if len(word) > 2 and word in product_name_lower:
                score += 10
                
        # Bonificación por productos activos y con stock
        if product.active:
            score += 5
            
        # Bonificación por precio definido
        if product.list_price > 0:
            score += 3
            
        return score

    def action_clear_search(self):
        """Limpiar búsqueda y resultados"""
        self.result_ids.unlink()
        self.interaction_ids.unlink()
        self.detected_brand = False
        self.detected_category = False
        self.search_performed = False
        self.needs_interaction = False
        self.interaction_completed = False
        self.state = 'draft'
        return True
        
    def _evaluate_search_quality(self):
        """Evaluar si la búsqueda necesita más información"""
        # Necesita interacción si:
        # 1. No se detectó marca ni categoría
        # 2. Se encontraron demasiados o muy pocos resultados
        # 3. Los resultados tienen baja relevancia promedio
        
        no_detection = not self.detected_brand and not self.detected_category
        too_many_results = self.result_count > 50
        too_few_results = self.result_count == 0
        
        if self.result_count > 0:
            avg_relevance = sum(r.relevance_score for r in self.result_ids) / self.result_count
            low_relevance = avg_relevance < 30
        else:
            low_relevance = True
            
        return no_detection or too_many_results or too_few_results or low_relevance

    def _apply_learned_patterns(self):
        """Aplicar patrones aprendidos de búsquedas anteriores"""
        pattern = self.env['product.search.learning.pattern'].find_matching_pattern(self.query_text)
        if pattern and pattern.learning_data:
            try:
                import json
                learned_data = json.loads(pattern.learning_data)
                
                # Aplicar marca aprendida si no se detectó
                if not self.detected_brand and learned_data.get('preferred_brand'):
                    self.detected_brand = learned_data['preferred_brand']
                    
                # Aplicar categoría aprendida si no se detectó  
                if not self.detected_category and learned_data.get('preferred_category'):
                    self.detected_category = learned_data['preferred_category']
                    
                # Actualizar contador de uso del patrón
                pattern.usage_count += 1
                pattern.last_used = fields.Datetime.now()
                    
            except Exception as e:
                import logging
                _logger = logging.getLogger(__name__)
                _logger.warning(f"Error aplicando patrones aprendidos: {e}")

    def _show_interaction_wizard(self):
        """Mostrar wizard de interacción conversacional"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Búsqueda Conversacional',
            'res_model': 'product.search.interaction.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_search_id': self.id,
            }
        }

    def action_process_interactions(self):
        """Procesar respuestas de interacción y reejecutar búsqueda"""
        self.ensure_one()
        
        # Aplicar respuestas a la detección
        for interaction in self.interaction_ids.filtered('is_answered'):
            if interaction.question_type == 'brand' and interaction.user_answer != 'no_preference':
                self.detected_brand = interaction.user_answer
                
            elif interaction.question_type == 'category':
                self.detected_category = interaction.user_answer
                
        # Guardar datos de aprendizaje
        self._save_learning_data()
        
        # Reejecutar búsqueda con nueva información
        self.needs_interaction = False
        self.interaction_completed = True
        
        # Limpiar resultados anteriores
        self.result_ids.unlink()
        
        # Buscar con información mejorada
        products = self._search_products_enhanced()
        self._create_search_results(products)
        
        self.state = 'done' if self.result_count > 0 else 'no_results'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': '✅ Búsqueda Actualizada',
                'message': f'Se encontraron {self.result_count} productos con la información adicional.',
                'type': 'success',
            }
        }

    def _save_learning_data(self):
        """Guardar datos para aprender de esta interacción"""
        import json
        learning_data = {}
        
        for interaction in self.interaction_ids.filtered('is_answered'):
            if interaction.question_type == 'brand':
                learning_data['preferred_brand'] = interaction.user_answer
            elif interaction.question_type == 'category':
                learning_data['preferred_category'] = interaction.user_answer
                
        # Guardar en el registro actual
        self.learning_data = json.dumps(learning_data)
        
        # Crear patrón global para futuras búsquedas similares
        self._create_global_learning_pattern(learning_data)

    def _create_global_learning_pattern(self, learning_data):
        """Crear patrón global de aprendizaje"""
        import json
        pattern = self.env['product.search.learning.pattern'].create({
            'query_keywords': ' '.join(self.query_text.lower().split()[:5]),  # Primeras 5 palabras
            'detected_brand': self.detected_brand,
            'detected_category': self.detected_category,
            'learning_data': json.dumps(learning_data),
            'usage_count': 1,
        })
        return pattern

    def _search_products_enhanced(self):
        """Búsqueda mejorada con información de interacciones"""
        domain = []
        
        # Aplicar filtros basados en interacciones
        for interaction in self.interaction_ids.filtered('is_answered'):
            if interaction.question_type == 'price_range' and interaction.user_answer != 'no_preference':
                price_range = interaction.user_answer
                if price_range == '0-500':
                    domain.append(('list_price', '<=', 500))
                elif price_range == '500-1500':
                    domain.extend([('list_price', '>', 500), ('list_price', '<=', 1500)])
                elif price_range == '1500-5000':
                    domain.extend([('list_price', '>', 1500), ('list_price', '<=', 5000)])
                elif price_range == '5000+':
                    domain.append(('list_price', '>', 5000))
                    
        # Buscar con el dominio base + filtros de interacción
        base_domain = self._build_base_search_domain()
        final_domain = base_domain + domain
        
        products = self.env['product.template'].search(final_domain, limit=30)
        return products

    def _build_base_search_domain(self):
        """Construir dominio base de búsqueda"""
        domain = []
        
        # Aplicar marca detectada o aprendida
        if self.detected_brand:
            domain.append('|')
            domain.append(('name', 'ilike', self.detected_brand))
            domain.append(('default_code', 'ilike', self.detected_brand))
            
        # Aplicar categoría detectada o aprendida
        if self.detected_category:
            if domain:
                domain.insert(0, '&')
            domain.append('|')
            domain.append(('categ_id.name', 'ilike', self.detected_category))
            domain.append(('name', 'ilike', self.detected_category))
            
        # Si no hay información específica, usar palabras clave
        if not domain:
            words = self.query_text.split()
            stop_words = ['el', 'la', 'de', 'para', 'con', 'un', 'una', 'que', 'es', 'en', 'y', 'a']
            keywords = [word for word in words if len(word) > 2 and word.lower() not in stop_words]
            
            if keywords:
                domain = ['|'] * (len(keywords) - 1)
                for keyword in keywords:
                    domain.append(('name', 'ilike', keyword))
                    
        return domain if domain else [('active', '=', True)]
