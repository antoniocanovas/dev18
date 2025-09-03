from odoo import models, fields, api
import json


class ProductSearchInteractionWizard(models.TransientModel):
    _name = 'product.search.interaction.wizard'
    _description = 'Wizard de Interacción Conversacional'

    search_id = fields.Many2one(
        'product.search',
        string='Búsqueda',
        required=True
    )
    current_interaction_id = fields.Many2one(
        'product.search.interaction',
        string='Pregunta Actual'
    )
    current_question = fields.Text(
        string='Pregunta',
        related='current_interaction_id.question_text',
        readonly=True
    )
    current_question_type = fields.Selection(
        string='Tipo',
        related='current_interaction_id.question_type',
        readonly=True
    )
    
    # Campos de respuesta según tipo
    brand_answer = fields.Selection([
        ('HP', 'HP'),
        ('Dell', 'Dell'),
        ('Lenovo', 'Lenovo'),
        ('Apple', 'Apple'),
        ('Samsung', 'Samsung'),
        ('Sony', 'Sony'),
        ('LG', 'LG'),
        ('ASUS', 'ASUS'),
        ('Acer', 'Acer'),
        ('Canon', 'Canon'),
        ('Epson', 'Epson'),
        ('no_preference', 'Sin preferencia')
    ], string='Marca Preferida')
    
    category_answer = fields.Selection([
        ('laptop', 'Laptop/Computadora Portátil'),
        ('desktop', 'Computadora de Escritorio'),
        ('smartphone', 'Teléfono/Smartphone'),
        ('tablet', 'Tablet'),
        ('monitor', 'Monitor/Pantalla'),
        ('printer', 'Impresora'),
        ('keyboard', 'Teclado'),
        ('mouse', 'Mouse'),
        ('headphones', 'Audífonos'),
        ('camera', 'Cámara'),
        ('other', 'Otro')
    ], string='Categoría')
    
    price_range_answer = fields.Selection([
        ('0-500', 'Económico (hasta $500)'),
        ('500-1500', 'Medio ($500 - $1,500)'),
        ('1500-5000', 'Premium ($1,500 - $5,000)'),
        ('5000+', 'Sin límite ($5,000+)')
    ], string='Rango de Precio')
    
    usage_answer = fields.Selection([
        ('gaming', '🎮 Gaming/Juegos'),
        ('work', '💼 Trabajo/Oficina'),
        ('home', '🏠 Uso doméstico'),
        ('study', '📚 Estudios'),
        ('professional', '🎯 Uso profesional'),
        ('other', '🔧 Otro')
    ], string='Uso Previsto')
    
    text_answer = fields.Text(
        string='Otra Respuesta',
        placeholder='Describe lo que buscas con más detalle...'
    )
    
    # Control de flujo
    total_questions = fields.Integer(
        string='Total de Preguntas',
        compute='_compute_total_questions'
    )
    current_question_number = fields.Integer(
        string='Pregunta Actual',
        default=1
    )
    progress_percentage = fields.Float(
        string='Progreso %',
        compute='_compute_progress'
    )
    
    # Chat log
    conversation_log = fields.Html(
        string='Conversación',
        compute='_compute_conversation_log'
    )

    @api.depends('search_id.interaction_ids')
    def _compute_total_questions(self):
        for wizard in self:
            wizard.total_questions = len(wizard.search_id.interaction_ids)

    @api.depends('current_question_number', 'total_questions')
    def _compute_progress(self):
        for wizard in self:
            if wizard.total_questions > 0:
                wizard.progress_percentage = (wizard.current_question_number / wizard.total_questions) * 100
            else:
                wizard.progress_percentage = 0

    @api.depends('search_id.interaction_ids.is_answered', 'current_interaction_id')
    def _compute_conversation_log(self):
        for wizard in self:
            log_html = f"""
            <div class="conversation-container">
                <div class="original-query">
                    <strong>🤖 Sistema:</strong> Estás buscando: "<em>{wizard.search_id.query_text}</em>"
                </div>
            """
            
            for interaction in wizard.search_id.interaction_ids.sorted('sequence'):
                if interaction.is_answered:
                    log_html += f"""
                    <div class="question-answered">
                        <div class="bot-question">🤖 <strong>Sistema:</strong> {interaction.question_text}</div>
                        <div class="user-answer">👤 <strong>Tu respuesta:</strong> {interaction.user_answer}</div>
                    </div>
                    """
                elif interaction == wizard.current_interaction_id:
                    log_html += f"""
                    <div class="current-question">
                        <div class="bot-question current">🤖 <strong>Sistema:</strong> {interaction.question_text}</div>
                        <div class="typing">👤 Escribiendo...</div>
                    </div>
                    """
            
            log_html += "</div>"
            wizard.conversation_log = log_html

    @api.model
    def default_get(self, fields):
        """Configurar wizard con la primera pregunta"""
        res = super().default_get(fields)
        
        search_id = self.env.context.get('default_search_id')
        if search_id:
            search = self.env['product.search'].browse(search_id)
            first_interaction = search.interaction_ids.sorted('sequence')[:1]
            
            if first_interaction:
                res.update({
                    'search_id': search_id,
                    'current_interaction_id': first_interaction.id,
                    'current_question_number': 1
                })
        
        return res

    def action_answer_question(self):
        """Procesar respuesta actual y avanzar"""
        self.ensure_one()
        
        if not self.current_interaction_id:
            return self._finish_interaction()
        
        # Obtener la respuesta según el tipo de pregunta
        answer = self._get_current_answer()
        
        if not answer:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': '⚠️ Respuesta Requerida',
                    'message': 'Por favor selecciona o escribe una respuesta.',
                    'type': 'warning',
                }
            }
        
        # Guardar respuesta
        self.current_interaction_id.write({
            'user_answer': answer,
            'is_answered': True
        })
        
        # Buscar siguiente pregunta
        next_interaction = self.search_id.interaction_ids.filtered(
            lambda i: not i.is_answered
        ).sorted('sequence')[:1]
        
        if next_interaction:
            # Continuar con siguiente pregunta
            self.write({
                'current_interaction_id': next_interaction.id,
                'current_question_number': self.current_question_number + 1
            })
            
            # Limpiar respuestas anteriores
            self._clear_answer_fields()
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'product.search.interaction.wizard',
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
                'context': self.env.context
            }
        else:
            # Terminar interacción
            return self._finish_interaction()

    def _get_current_answer(self):
        """Obtener respuesta actual según el tipo de pregunta"""
        if self.current_question_type == 'brand':
            return self.brand_answer
        elif self.current_question_type == 'category':
            return self.category_answer
        elif self.current_question_type == 'price_range':
            return self.price_range_answer
        elif self.current_question_type == 'usage':
            return self.usage_answer
        else:
            return self.text_answer

    def _clear_answer_fields(self):
        """Limpiar campos de respuesta para la siguiente pregunta"""
        self.write({
            'brand_answer': False,
            'category_answer': False,
            'price_range_answer': False,
            'usage_answer': False,
            'text_answer': False
        })

    def _finish_interaction(self):
        """Finalizar interacción y reejecutar búsqueda"""
        # Procesar todas las respuestas
        self.search_id.action_process_interactions()
        
        # Mostrar resultados finales
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.search',
            'res_id': self.search_id.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'search_completed': True
            }
        }

    def action_skip_question(self):
        """Saltar pregunta actual"""
        self.ensure_one()
        
        if self.current_interaction_id:
            self.current_interaction_id.write({
                'user_answer': 'Sin respuesta',
                'is_answered': True
            })
        
        return self.action_answer_question()

    def action_finish_early(self):
        """Terminar interacción temprano con respuestas parciales"""
        self.ensure_one()
        
        # Marcar preguntas restantes como omitidas
        remaining_interactions = self.search_id.interaction_ids.filtered(
            lambda i: not i.is_answered
        )
        
        for interaction in remaining_interactions:
            interaction.write({
                'user_answer': 'Omitida',
                'is_answered': True
            })
        
        return self._finish_interaction()
