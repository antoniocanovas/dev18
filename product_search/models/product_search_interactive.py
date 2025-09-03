from odoo import models, fields, api
from odoo.exceptions import UserError
import json
import logging

_logger = logging.getLogger(__name__)


class ProductSearchInteraction(models.Model):
    _name = 'product.search.interaction'
    _description = 'Interacción de Búsqueda Conversacional'
    _order = 'sequence, id'

    search_id = fields.Many2one(
        'product.search',
        string='Búsqueda',
        required=True,
        ondelete='cascade'
    )
    sequence = fields.Integer(
        string='Secuencia',
        default=10
    )
    question_type = fields.Selection([
        ('brand', 'Marca'),
        ('category', 'Categoría'),
        ('price_range', 'Rango de Precio'),
        ('features', 'Características'),
        ('usage', 'Uso Previsto'),
        ('confirmation', 'Confirmación')
    ], string='Tipo de Pregunta', required=True)
    
    question_text = fields.Text(
        string='Pregunta',
        required=True
    )
    suggested_answers = fields.Text(
        string='Respuestas Sugeridas (JSON)',
        help='Lista de opciones sugeridas en formato JSON'
    )
    user_answer = fields.Text(
        string='Respuesta del Usuario'
    )
    is_answered = fields.Boolean(
        string='Respondida',
        default=False
    )
    confidence_score = fields.Float(
        string='Puntuación de Confianza',
        digits=(3, 2),
        help='Qué tan seguro está el sistema de esta respuesta'
    )

    @api.model
    def generate_questions_for_search(self, search_id):
        """Generar preguntas inteligentes basadas en la búsqueda"""
        search = self.env['product.search'].browse(search_id)
        questions = []
        
        # Limpiar interacciones anteriores
        search.interaction_ids.unlink()
        
        # Pregunta por marca si no se detectó
        if not search.detected_brand:
            brand_suggestions = self._get_brand_suggestions(search.query_text)
            questions.append({
                'search_id': search_id,
                'sequence': 10,
                'question_type': 'brand',
                'question_text': f'No pude identificar una marca específica en "{search.query_text}". ¿Qué marca prefieres?',
                'suggested_answers': json.dumps(brand_suggestions)
            })
        
        # Pregunta por categoría si no se detectó
        if not search.detected_category:
            category_suggestions = self._get_category_suggestions(search.query_text)
            questions.append({
                'search_id': search_id,
                'sequence': 20,
                'question_type': 'category',
                'question_text': f'¿En qué categoría de productos estás interesado?',
                'suggested_answers': json.dumps(category_suggestions)
            })
            
        # Pregunta por rango de precio si hay muchos resultados
        if search.result_count > 20:
            questions.append({
                'search_id': search_id,
                'sequence': 30,
                'question_type': 'price_range',
                'question_text': 'Encontré muchos productos. ¿Cuál es tu rango de precio preferido?',
                'suggested_answers': json.dumps([
                    {'value': '0-500', 'label': 'Económico (hasta $500)'},
                    {'value': '500-1500', 'label': 'Medio ($500 - $1,500)'},
                    {'value': '1500-5000', 'label': 'Premium ($1,500 - $5,000)'},
                    {'value': '5000+', 'label': 'Sin límite ($5,000+)'}
                ])
            })
            
        # Pregunta por uso específico
        usage_keywords = ['gaming', 'oficina', 'casa', 'profesional', 'estudiantes']
        if not any(keyword in search.query_text.lower() for keyword in usage_keywords):
            questions.append({
                'search_id': search_id,
                'sequence': 40,
                'question_type': 'usage',
                'question_text': '¿Para qué vas a usar principalmente este producto?',
                'suggested_answers': json.dumps([
                    {'value': 'gaming', 'label': '🎮 Gaming/Juegos'},
                    {'value': 'work', 'label': '💼 Trabajo/Oficina'},
                    {'value': 'home', 'label': '🏠 Uso doméstico'},
                    {'value': 'study', 'label': '📚 Estudios'},
                    {'value': 'professional', 'label': '🎯 Uso profesional'},
                    {'value': 'other', 'label': '🔧 Otro'}
                ])
            })
        
        # Crear registros de interacción
        for question_data in questions:
            self.create(question_data)
            
        return len(questions)

    def _get_brand_suggestions(self, query_text):
        """Obtener sugerencias de marcas basadas en productos existentes"""
        # Buscar marcas más comunes en el inventario
        brands_query = """
            SELECT DISTINCT 
                CASE 
                    WHEN name ILIKE '%HP%' THEN 'HP'
                    WHEN name ILIKE '%Dell%' THEN 'Dell'
                    WHEN name ILIKE '%Lenovo%' THEN 'Lenovo'
                    WHEN name ILIKE '%Apple%' THEN 'Apple'
                    WHEN name ILIKE '%Samsung%' THEN 'Samsung'
                    WHEN name ILIKE '%Sony%' THEN 'Sony'
                    WHEN name ILIKE '%LG%' THEN 'LG'
                    WHEN name ILIKE '%ASUS%' THEN 'ASUS'
                    WHEN name ILIKE '%Acer%' THEN 'Acer'
                    WHEN name ILIKE '%Canon%' THEN 'Canon'
                    WHEN name ILIKE '%Epson%' THEN 'Epson'
                END as brand,
                COUNT(*) as product_count
            FROM product_template 
            WHERE active = true
            AND (name ILIKE '%HP%' OR name ILIKE '%Dell%' OR name ILIKE '%Lenovo%' 
                OR name ILIKE '%Apple%' OR name ILIKE '%Samsung%' OR name ILIKE '%Sony%'
                OR name ILIKE '%LG%' OR name ILIKE '%ASUS%' OR name ILIKE '%Acer%'
                OR name ILIKE '%Canon%' OR name ILIKE '%Epson%')
            GROUP BY brand
            ORDER BY product_count DESC
            LIMIT 8
        """
        
        self.env.cr.execute(brands_query)
        results = self.env.cr.fetchall()
        
        suggestions = [{'value': brand, 'label': f'{brand} ({count} productos)'} 
                      for brand, count in results if brand]
        
        # Agregar opción "Sin preferencia"
        suggestions.append({'value': 'no_preference', 'label': '🤷 Sin preferencia de marca'})
        
        return suggestions

    def _get_category_suggestions(self, query_text):
        """Obtener sugerencias de categorías"""
        # Buscar categorías más comunes
        categories_query = """
            SELECT pc.name, COUNT(pt.id) as product_count
            FROM product_category pc
            JOIN product_template pt ON pt.categ_id = pc.id
            WHERE pt.active = true
            GROUP BY pc.id, pc.name
            ORDER BY product_count DESC
            LIMIT 10
        """
        
        self.env.cr.execute(categories_query)
        results = self.env.cr.fetchall()
        
        suggestions = [{'value': name.lower(), 'label': f'{name} ({count} productos)'} 
                      for name, count in results]
        
        return suggestions


class ProductSearchLearningPattern(models.Model):
    _name = 'product.search.learning.pattern'
    _description = 'Patrón de Aprendizaje de Búsquedas'
    _order = 'usage_count desc, create_date desc'

    query_keywords = fields.Char(
        string='Palabras Clave',
        required=True,
        index=True
    )
    detected_brand = fields.Char(
        string='Marca Detectada'
    )
    detected_category = fields.Char(
        string='Categoría Detectada'
    )
    learning_data = fields.Text(
        string='Datos Aprendidos',
        help='JSON con información aprendida de interacciones'
    )
    usage_count = fields.Integer(
        string='Veces Usado',
        default=1
    )
    success_rate = fields.Float(
        string='Tasa de Éxito (%)',
        digits=(5, 2),
        help='Porcentaje de búsquedas exitosas con este patrón'
    )
    last_used = fields.Datetime(
        string='Último Uso',
        default=fields.Datetime.now
    )

    @api.model
    def find_matching_pattern(self, query_text):
        """Encontrar patrón coincidente para aplicar aprendizaje"""
        query_words = set(query_text.lower().split())
        
        patterns = self.search([])
        best_match = None
        best_score = 0
        
        for pattern in patterns:
            pattern_words = set(pattern.query_keywords.split())
            
            # Calcular similitud usando intersección de palabras
            intersection = query_words.intersection(pattern_words)
            union = query_words.union(pattern_words)
            
            if len(union) > 0:
                similarity = len(intersection) / len(union)
                
                # Bonus por uso frecuente
                usage_bonus = min(pattern.usage_count / 100, 0.2)
                total_score = similarity + usage_bonus
                
                if total_score > best_score and similarity > 0.3:
                    best_score = total_score
                    best_match = pattern
        
        return best_match
