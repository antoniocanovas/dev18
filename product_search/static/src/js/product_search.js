/* ============================================
   JavaScript para Búsqueda Inteligente de Productos
   ============================================ */

odoo.define('product_search.interaction', function (require) {
    "use strict";
    
    var FormController = require('web.FormController');
    var FormRenderer = require('web.FormRenderer');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    
    var _t = core._t;

    // Extender FormController para búsquedas de productos
    var ProductSearchFormController = FormController.extend({
        
        /**
         * Ejecutar búsqueda con animaciones
         */
        _onSearchProducts: function() {
            var self = this;
            
            // Mostrar indicador de carga
            this._showSearchingAnimation();
            
            // Ejecutar búsqueda original
            return this._super.apply(this, arguments).then(function(result) {
                self._hideSearchingAnimation();
                
                // Si hay interacción necesaria, mostrar wizard animado
                if (self.model.data.needs_interaction) {
                    self._showConversationalWizard();
                }
                
                return result;
            });
        },
        
        /**
         * Mostrar animación de búsqueda
         */
        _showSearchingAnimation: function() {
            var $button = this.$('.btn-search');
            var originalText = $button.text();
            
            $button
                .prop('disabled', true)
                .html('<i class="fa fa-spinner fa-spin"></i> Buscando...')
                .addClass('btn-loading');
                
            // Crear efecto de pulso en el contenedor
            this.$('.product-search-container').addClass('searching-pulse');
        },
        
        /**
         * Ocultar animación de búsqueda
         */
        _hideSearchingAnimation: function() {
            var $button = this.$('.btn-search');
            
            $button
                .prop('disabled', false)
                .html('🔍 Buscar Productos')
                .removeClass('btn-loading');
                
            this.$('.product-search-container').removeClass('searching-pulse');
        },
        
        /**
         * Mostrar wizard conversacional con efectos
         */
        _showConversationalWizard: function() {
            var self = this;
            
            // Crear notificación atractiva
            this.displayNotification({
                title: _t('💬 Búsqueda Conversacional'),
                message: _t('El sistema necesita más información para encontrar mejores resultados. ¡Te ayudo con unas preguntas!'),
                type: 'info',
                sticky: false,
            });
            
            // Agregar efectos visuales
            setTimeout(function() {
                self.$('.oe_chatter').addClass('conversation-highlight');
            }, 1000);
        }
    });

    // Extender FormRenderer para efectos visuales
    var ProductSearchFormRenderer = FormRenderer.extend({
        
        /**
         * Después de renderizar, agregar efectos
         */
        _renderView: function() {
            var result = this._super.apply(this, arguments);
            this._addVisualEffects();
            return result;
        },
        
        /**
         * Agregar efectos visuales a elementos
         */
        _addVisualEffects: function() {
            var self = this;
            
            // Animar resultados de búsqueda cuando aparecen
            this.$('.search-result-card').each(function(index) {
                $(this).css({
                    'opacity': '0',
                    'transform': 'translateY(20px)'
                }).delay(index * 100).animate({
                    'opacity': '1',
                    'transform': 'translateY(0)'
                }, 500);
            });
            
            // Efectos hover en tarjetas de resultado
            this.$('.search-result-card').hover(
                function() {
                    $(this).addClass('card-hover-effect');
                },
                function() {
                    $(this).removeClass('card-hover-effect');
                }
            );
            
            // Actualizar barras de progreso de relevancia
            this._updateRelevanceBars();
            
            // Agregar tooltips informativos
            this._addInformativeTooltips();
        },
        
        /**
         * Actualizar barras de relevancia con animación
         */
        _updateRelevanceBars: function() {
            this.$('.relevance-indicator').each(function() {
                var $indicator = $(this);
                var score = parseFloat($indicator.data('score')) || 0;
                var percentage = Math.max(10, score); // Mínimo 10% para visibilidad
                
                var $fill = $indicator.find('.relevance-fill');
                if ($fill.length === 0) {
                    $fill = $('<div class="relevance-fill"></div>');
                    $indicator.append($fill);
                }
                
                // Animar la barra
                setTimeout(function() {
                    $fill.css('width', percentage + '%');
                }, 200);
            });
        },
        
        /**
         * Agregar tooltips informativos
         */
        _addInformativeTooltips: function() {
            // Tooltip para marca detectada
            this.$('[data-field="detected_brand"]').attr('title', 
                _t('Marca detectada automáticamente del texto de búsqueda')
            );
            
            // Tooltip para categoría detectada
            this.$('[data-field="detected_category"]').attr('title', 
                _t('Categoría identificada automáticamente')
            );
            
            // Tooltip para puntuación de relevancia
            this.$('.relevance-score').attr('title', 
                _t('Puntuación calculada basada en coincidencias con tu búsqueda')
            );
        }
    });

    // Widget para el wizard conversacional
    var ConversationalWizard = Dialog.extend({
        template: 'ProductSearch.ConversationalWizard',
        
        events: {
            'click .btn-answer': '_onAnswerClick',
            'click .btn-skip': '_onSkipClick',
            'click .btn-finish': '_onFinishEarly',
            'change input[type="radio"]': '_onAnswerChange',
        },
        
        init: function(parent, options) {
            options = options || {};
            this.searchId = options.searchId;
            this.currentQuestion = options.currentQuestion;
            this.totalQuestions = options.totalQuestions || 1;
            this.questionNumber = options.questionNumber || 1;
            
            this._super(parent, _.extend({
                title: _t('🤖 Búsqueda Conversacional'),
                size: 'medium',
                buttons: [
                    {
                        text: _t('Continuar'),
                        classes: 'btn-primary btn-conversation',
                        click: this._onAnswerClick.bind(this),
                    },
                    {
                        text: _t('Omitir'),
                        classes: 'btn-secondary',
                        click: this._onSkipClick.bind(this),
                    },
                    {
                        text: _t('Cancelar'),
                        close: true,
                    }
                ]
            }, options));
        },
        
        start: function() {
            var result = this._super.apply(this, arguments);
            this._updateProgressBar();
            this._addTypingAnimation();
            return result;
        },
        
        /**
         * Actualizar barra de progreso
         */
        _updateProgressBar: function() {
            var progress = (this.questionNumber / this.totalQuestions) * 100;
            this.$('.progress-bar-modern').css('width', progress + '%');
            this.$('.question-counter').text(this.questionNumber + ' de ' + this.totalQuestions);
        },
        
        /**
         * Agregar animación de escritura
         */
        _addTypingAnimation: function() {
            var $question = this.$('.bot-question');
            var text = $question.text();
            
            $question.empty();
            
            // Efecto de escritura
            var i = 0;
            var typeWriter = function() {
                if (i < text.length) {
                    $question.text($question.text() + text.charAt(i));
                    i++;
                    setTimeout(typeWriter, 30);
                }
            };
            
            setTimeout(typeWriter, 500);
        },
        
        /**
         * Manejar respuesta del usuario
         */
        _onAnswerClick: function() {
            var answer = this._getCurrentAnswer();
            
            if (!answer) {
                this.displayNotification({
                    title: _t('Respuesta requerida'),
                    message: _t('Por favor selecciona una respuesta antes de continuar.'),
                    type: 'warning'
                });
                return;
            }
            
            // Animar respuesta del usuario
            this._animateUserResponse(answer);
            
            // Procesar respuesta
            this._processAnswer(answer);
        },
        
        /**
         * Animar respuesta del usuario
         */
        _animateUserResponse: function(answer) {
            var $userResponse = $('<div class="user-answer">')
                .text('👤 ' + answer)
                .css('opacity', '0');
                
            this.$('.conversation-log').append($userResponse);
            
            $userResponse.animate({'opacity': '1'}, 500);
        },
        
        /**
         * Obtener respuesta actual
         */
        _getCurrentAnswer: function() {
            return this.$('input[type="radio"]:checked').val() || 
                   this.$('textarea').val() || 
                   this.$('input[type="text"]').val();
        },
        
        /**
         * Procesar respuesta y continuar
         */
        _processAnswer: function(answer) {
            // Aquí se llamaría al método del controlador para procesar la respuesta
            // y mostrar la siguiente pregunta o finalizar
            this.close();
        }
    });

    // Utilidades para efectos visuales
    var VisualEffects = {
        
        /**
         * Crear efecto de partículas para celebrar resultados exitosos
         */
        createSuccessParticles: function($container) {
            if (!$container || $container.length === 0) return;
            
            var colors = ['#28a745', '#20c997', '#17a2b8', '#007bff'];
            
            for (var i = 0; i < 10; i++) {
                var $particle = $('<div class="success-particle">')
                    .css({
                        position: 'absolute',
                        width: '6px',
                        height: '6px',
                        background: colors[Math.floor(Math.random() * colors.length)],
                        borderRadius: '50%',
                        top: '50%',
                        left: '50%',
                        opacity: '1'
                    });
                    
                $container.append($particle);
                
                // Animar partícula
                $particle.animate({
                    top: Math.random() * 100 + '%',
                    left: Math.random() * 100 + '%',
                    opacity: 0
                }, 2000, function() {
                    $(this).remove();
                });
            }
        },
        
        /**
         * Efecto de ondas para indicar actividad
         */
        createRippleEffect: function($element, event) {
            var $ripple = $('<div class="ripple-effect">');
            var offset = $element.offset();
            var x = event.pageX - offset.left;
            var y = event.pageY - offset.top;
            
            $ripple.css({
                position: 'absolute',
                width: '2px',
                height: '2px',
                background: 'rgba(255,255,255,0.6)',
                borderRadius: '50%',
                left: x,
                top: y,
                transform: 'scale(0)',
                pointerEvents: 'none'
            });
            
            $element.append($ripple);
            
            $ripple.animate({
                transform: 'scale(50)',
                opacity: 0
            }, 600, function() {
                $(this).remove();
            });
        }
    };

    // Registrar widgets personalizados
    core.action_registry.add('product_search_conversation', ConversationalWizard);
    
    return {
        ProductSearchFormController: ProductSearchFormController,
        ProductSearchFormRenderer: ProductSearchFormRenderer,
        ConversationalWizard: ConversationalWizard,
        VisualEffects: VisualEffects
    };
    
});

/* ============================================
   Funciones JavaScript puras para mejorar UX
   ============================================ */

// Función para mejorar la búsqueda en tiempo real
function enhanceSearchInput() {
    document.addEventListener('DOMContentLoaded', function() {
        var searchInputs = document.querySelectorAll('textarea[name="query_text"]');
        
        searchInputs.forEach(function(input) {
            // Agregar contador de caracteres
            var counter = document.createElement('small');
            counter.className = 'text-muted char-counter';
            input.parentNode.appendChild(counter);
            
            // Actualizar contador
            function updateCounter() {
                var length = input.value.length;
                counter.textContent = length + ' caracteres';
                
                if (length > 10) {
                    counter.style.color = '#28a745';
                } else {
                    counter.style.color = '#ffc107';
                }
            }
            
            input.addEventListener('input', updateCounter);
            updateCounter();
            
            // Sugerencias mientras escribe
            input.addEventListener('input', debounce(showSearchSuggestions, 300));
        });
    });
}

// Función para mostrar sugerencias de búsqueda
function showSearchSuggestions(event) {
    var input = event.target;
    var text = input.value.toLowerCase();
    
    // Ejemplos de sugerencias basadas en palabras clave
    var suggestions = {
        'laptop': ['Laptop HP gaming', 'Laptop Dell para trabajo', 'Laptop Apple MacBook'],
        'telefono': ['Teléfono Samsung Galaxy', 'Teléfono iPhone Apple', 'Teléfono Xiaomi económico'],
        'monitor': ['Monitor 4K para diseño', 'Monitor gaming curvo', 'Monitor Dell UltraSharp'],
        'gaming': ['Gaming laptop HP', 'Gaming mouse RGB', 'Gaming keyboard mecánico']
    };
    
    // Buscar sugerencias
    var foundSuggestions = [];
    Object.keys(suggestions).forEach(function(key) {
        if (text.includes(key)) {
            foundSuggestions = foundSuggestions.concat(suggestions[key]);
        }
    });
    
    if (foundSuggestions.length > 0) {
        showSuggestionDropdown(input, foundSuggestions.slice(0, 3));
    }
}

// Mostrar dropdown de sugerencias
function showSuggestionDropdown(input, suggestions) {
    // Remover dropdown existente
    var existingDropdown = document.querySelector('.search-suggestions-dropdown');
    if (existingDropdown) {
        existingDropdown.remove();
    }
    
    // Crear nuevo dropdown
    var dropdown = document.createElement('div');
    dropdown.className = 'search-suggestions-dropdown';
    dropdown.style.cssText = `
        position: absolute;
        background: white;
        border: 1px solid #ddd;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        z-index: 1000;
        max-width: 300px;
        margin-top: 5px;
    `;
    
    suggestions.forEach(function(suggestion) {
        var item = document.createElement('div');
        item.className = 'suggestion-item';
        item.textContent = suggestion;
        item.style.cssText = `
            padding: 10px 15px;
            cursor: pointer;
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.2s;
        `;
        
        item.addEventListener('mouseenter', function() {
            this.style.background = '#f8f9fa';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.background = 'white';
        });
        
        item.addEventListener('click', function() {
            input.value = suggestion;
            dropdown.remove();
            input.dispatchEvent(new Event('change'));
        });
        
        dropdown.appendChild(item);
    });
    
    // Posicionar dropdown
    input.parentNode.style.position = 'relative';
    input.parentNode.appendChild(dropdown);
}

// Función debounce para optimizar rendimiento
function debounce(func, wait) {
    var timeout;
    return function executedFunction() {
        var context = this;
        var args = arguments;
        
        var later = function() {
            clearTimeout(timeout);
            func.apply(context, args);
        };
        
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Función para mejorar la visualización de resultados
function enhanceSearchResults() {
    document.addEventListener('DOMContentLoaded', function() {
        // Agregar animaciones de aparición a los resultados
        var resultCards = document.querySelectorAll('.search-result-card');
        
        resultCards.forEach(function(card, index) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            setTimeout(function() {
                card.style.transition = 'all 0.5s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
        
        // Mejorar interacción con botones de acción
        var actionButtons = document.querySelectorAll('.btn-primary, .btn-success');
        actionButtons.forEach(function(button) {
            button.addEventListener('click', function(e) {
                // Efecto de ondas
                createRippleEffect(this, e);
            });
        });
    });
}

function createRippleEffect(element, event) {
    var ripple = document.createElement('span');
    var rect = element.getBoundingClientRect();
    var x = event.clientX - rect.left;
    var y = event.clientY - rect.top;
    
    ripple.style.cssText = `
        position: absolute;
        width: 4px;
        height: 4px;
        background: rgba(255,255,255,0.6);
        border-radius: 50%;
        left: ${x}px;
        top: ${y}px;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    `;
    
    element.appendChild(ripple);
    
    setTimeout(function() {
        ripple.remove();
    }, 600);
}

// CSS para animación de ondas (si no está ya definido)
if (!document.querySelector('#ripple-animation-styles')) {
    var style = document.createElement('style');
    style.id = 'ripple-animation-styles';
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(20);
                opacity: 0;
            }
        }
        
        .btn-primary, .btn-success {
            position: relative;
            overflow: hidden;
        }
    `;
    document.head.appendChild(style);
}

// Inicializar mejoras
enhanceSearchInput();
enhanceSearchResults();