"""
🔍 Ejemplos Básicos de Búsqueda Inteligente de Productos

Estos ejemplos muestran cómo usar el módulo de Búsqueda Inteligente
desde código Python dentro de Odoo.

Para ejecutar: Copiar y pegar en el shell de Odoo o en un método personalizado.
"""

# ============================================
# EJEMPLO 1: Búsqueda Simple
# ============================================

def ejemplo_busqueda_simple():
    """Crear y ejecutar una búsqueda básica"""
    
    # Crear nueva búsqueda
    search = env['product.search'].create({
        'query_text': 'Laptop HP para gaming'
    })
    
    print(f"Búsqueda creada: {search.name}")
    
    # Ejecutar búsqueda
    search.action_search_products()
    
    print(f"Estado: {search.state}")
    print(f"Marca detectada: {search.detected_brand}")
    print(f"Categoría detectada: {search.detected_category}")
    print(f"Productos encontrados: {search.result_count}")
    
    # Mostrar resultados
    for result in search.result_ids[:5]:  # Primeros 5 resultados
        print(f"- {result.product_name}: {result.relevance_score} puntos")
    
    return search

# Ejecutar ejemplo
# search_example = ejemplo_busqueda_simple()


# ============================================
# EJEMPLO 2: Búsqueda con Análisis Detallado
# ============================================

def ejemplo_busqueda_detallada():
    """Análisis completo de una búsqueda"""
    
    search = env['product.search'].create({
        'query_text': 'Teléfono Samsung con buena cámara'
    })
    
    # Análisis antes de la búsqueda
    print("=== ANÁLISIS PRE-BÚSQUEDA ===")
    search._detect_brand_and_category()
    print(f"Marca detectada: {search.detected_brand}")
    print(f"Categoría detectada: {search.detected_category}")
    
    # Ejecutar búsqueda
    search.action_search_products()
    
    # Análisis después de la búsqueda
    print("\n=== ANÁLISIS POST-BÚSQUEDA ===")
    print(f"Estado final: {search.state}")
    print(f"¿Necesita conversación?: {search.needs_interaction}")
    
    if search.result_count > 0:
        # Estadísticas de relevancia
        scores = [r.relevance_score for r in search.result_ids]
        avg_score = sum(scores) / len(scores)
        max_score = max(scores)
        min_score = min(scores)
        
        print(f"\n=== ESTADÍSTICAS DE RELEVANCIA ===")
        print(f"Promedio: {avg_score:.1f} puntos")
        print(f"Máximo: {max_score:.1f} puntos")
        print(f"Mínimo: {min_score:.1f} puntos")
        
        # Distribución por nivel
        levels = {}
        for result in search.result_ids:
            level = result.relevance_level
            levels[level] = levels.get(level, 0) + 1
        
        print(f"\n=== DISTRIBUCIÓN POR NIVEL ===")
        for level, count in levels.items():
            print(f"{level.title()}: {count} productos")
    
    return search

# Ejecutar ejemplo
# detailed_search = ejemplo_busqueda_detallada()


# ============================================
# EJEMPLO 3: Búsqueda que Activa Conversación
# ============================================

def ejemplo_busqueda_conversacional():
    """Simular una búsqueda que requiere conversación"""
    
    # Búsqueda ambigua que activará el sistema conversacional
    search = env['product.search'].create({
        'query_text': 'Computadora para trabajar'
    })
    
    search.action_search_products()
    
    if search.needs_interaction:
        print("🤖 Sistema conversacional activado!")
        print(f"Preguntas generadas: {len(search.interaction_ids)}")
        
        # Mostrar preguntas generadas
        for interaction in search.interaction_ids.sorted('sequence'):
            print(f"\n{interaction.sequence}. {interaction.question_text}")
            if interaction.suggested_answers:
                import json
                answers = json.loads(interaction.suggested_answers)
                for answer in answers[:3]:  # Primeras 3 opciones
                    print(f"   - {answer.get('label', answer.get('value', answer))}")
        
        # Simular respuestas del usuario
        print("\n🧑 Simulando respuestas del usuario...")
        
        # Responder primera pregunta (marca)
        brand_question = search.interaction_ids.filtered(lambda i: i.question_type == 'brand')
        if brand_question:
            brand_question.write({
                'user_answer': 'HP',
                'is_answered': True
            })
            print("✅ Respondida pregunta de marca: HP")
        
        # Responder segunda pregunta (categoría)
        category_question = search.interaction_ids.filtered(lambda i: i.question_type == 'category')
        if category_question:
            category_question.write({
                'user_answer': 'laptop',
                'is_answered': True
            })
            print("✅ Respondida pregunta de categoría: laptop")
        
        # Procesar respuestas y reejecutar búsqueda
        search.action_process_interactions()
        
        print(f"\n🎉 Búsqueda mejorada completada!")
        print(f"Nuevos resultados: {search.result_count}")
        print(f"Marca aplicada: {search.detected_brand}")
        print(f"Categoría aplicada: {search.detected_category}")
    
    return search

# Ejecutar ejemplo
# conversational_search = ejemplo_busqueda_conversacional()


# ============================================
# EJEMPLO 4: Análisis de Patrones de Aprendizaje
# ============================================

def ejemplo_analisis_patrones():
    """Analizar patrones de aprendizaje existentes"""
    
    patterns = env['product.search.learning.pattern'].search([])
    
    print(f"=== PATRONES DE APRENDIZAJE ({len(patterns)} total) ===")
    
    if not patterns:
        print("ℹ️  No hay patrones de aprendizaje aún. Ejecuta algunas búsquedas conversacionales primero.")
        return
    
    # Patrones más usados
    top_patterns = patterns.sorted('usage_count', reverse=True)[:5]
    print(f"\n🔥 TOP 5 PATRONES MÁS USADOS:")
    for i, pattern in enumerate(top_patterns, 1):
        print(f"{i}. '{pattern.query_keywords}' - {pattern.usage_count} usos")
        print(f"   Marca: {pattern.detected_brand or 'N/A'}")
        print(f"   Categoría: {pattern.detected_category or 'N/A'}")
        print(f"   Éxito: {pattern.success_rate:.1f}%")
        print(f"   Último uso: {pattern.last_used}")
        print()
    
    # Estadísticas generales
    total_usage = sum(patterns.mapped('usage_count'))
    avg_success = sum(patterns.mapped('success_rate')) / len(patterns) if patterns else 0
    
    print(f"📊 ESTADÍSTICAS GENERALES:")
    print(f"Total de usos: {total_usage}")
    print(f"Éxito promedio: {avg_success:.1f}%")
    print(f"Patrones únicos: {len(patterns)}")
    
    # Marcas más aprendidas
    brands = {}
    for pattern in patterns:
        if pattern.detected_brand:
            brands[pattern.detected_brand] = brands.get(pattern.detected_brand, 0) + pattern.usage_count
    
    if brands:
        print(f"\n🏷️ MARCAS MÁS APRENDIDAS:")
        sorted_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:5]
        for brand, count in sorted_brands:
            print(f"- {brand}: {count} usos")

# Ejecutar ejemplo
# ejemplo_analisis_patrones()


# ============================================
# EJEMPLO 5: Búsquedas Programáticas en Lote
# ============================================

def ejemplo_busquedas_lote():
    """Ejecutar múltiples búsquedas programáticamente"""
    
    # Lista de consultas de ejemplo
    queries = [
        "Laptop HP gaming RTX",
        "Teléfono Samsung Galaxy",
        "Monitor Dell 4K",
        "Impresora Canon",
        "Mouse gaming RGB",
        "Teclado mecánico",
        "Auriculares Sony",
        "Tablet iPad",
        "Cámara Canon DSLR",
        "Disco duro SSD"
    ]
    
    results = []
    
    print("🚀 Ejecutando búsquedas en lote...")
    
    for i, query in enumerate(queries, 1):
        print(f"[{i}/{len(queries)}] Buscando: {query}")
        
        # Crear y ejecutar búsqueda
        search = env['product.search'].create({'query_text': query})
        search.action_search_products()
        
        # Recopilar estadísticas
        result_data = {
            'query': query,
            'brand': search.detected_brand,
            'category': search.detected_category,
            'results': search.result_count,
            'state': search.state,
            'needs_interaction': search.needs_interaction
        }
        
        results.append(result_data)
        
        # Log simple
        status = "✅" if search.result_count > 0 else "❌"
        interaction = " 🤖" if search.needs_interaction else ""
        print(f"   {status} {search.result_count} resultados{interaction}")
    
    # Análisis de resultados
    print(f"\n📊 RESUMEN DE BÚSQUEDAS EN LOTE:")
    
    successful = len([r for r in results if r['results'] > 0])
    with_interaction = len([r for r in results if r['needs_interaction']])
    with_brand = len([r for r in results if r['brand']])
    with_category = len([r for r in results if r['category']])
    
    print(f"Total búsquedas: {len(results)}")
    print(f"Exitosas: {successful} ({successful/len(results)*100:.1f}%)")
    print(f"Con conversación: {with_interaction} ({with_interaction/len(results)*100:.1f}%)")
    print(f"Marca detectada: {with_brand} ({with_brand/len(results)*100:.1f}%)")
    print(f"Categoría detectada: {with_category} ({with_category/len(results)*100:.1f}%)")
    
    return results

# Ejecutar ejemplo
# batch_results = ejemplo_busquedas_lote()


# ============================================
# EJEMPLO 6: Personalización de Detección
# ============================================

def ejemplo_personalizacion_deteccion():
    """Ejemplo de personalización del sistema de detección"""
    
    # Crear búsqueda para testing
    search = env['product.search'].create({
        'query_text': 'Smartphone Xiaomi Redmi para estudiantes'
    })
    
    print("=== DETECCIÓN ESTÁNDAR ===")
    search._detect_brand_and_category()
    print(f"Marca: {search.detected_brand}")
    print(f"Categoría: {search.detected_category}")
    
    # Simular detección personalizada (esto requeriría modificar el código real)
    print("\n=== SIMULANDO DETECCIÓN PERSONALIZADA ===")
    
    # Diccionarios extendidos (ejemplo de lo que se podría agregar)
    custom_brands = {
        'xiaomi': 'Xiaomi',
        'redmi': 'Xiaomi',
        'poco': 'POCO',
        'oneplus': 'OnePlus',
        'oppo': 'OPPO',
        'vivo': 'Vivo'
    }
    
    custom_categories = {
        'smartphone': 'Smartphone',
        'estudiantes': 'Educativo',
        'economico': 'Económico',
        'premium': 'Premium',
        'profesional': 'Profesional'
    }
    
    # Aplicar detección personalizada
    text = search.query_text.lower()
    
    detected_brand = None
    for brand_key, brand_value in custom_brands.items():
        if brand_key in text:
            detected_brand = brand_value
            break
    
    detected_category = None
    for cat_key, cat_value in custom_categories.items():
        if cat_key in text:
            detected_category = cat_value
            break
    
    print(f"Marca personalizada: {detected_brand}")
    print(f"Categoría personalizada: {detected_category}")
    
    # Aplicar detección personalizada
    if detected_brand:
        search.detected_brand = detected_brand
    if detected_category:
        search.detected_category = detected_category
    
    # Ejecutar búsqueda con detección personalizada
    search.action_search_products()
    
    print(f"\n=== RESULTADOS CON DETECCIÓN PERSONALIZADA ===")
    print(f"Productos encontrados: {search.result_count}")
    print(f"Estado: {search.state}")
    
    return search

# Ejecutar ejemplo
# custom_search = ejemplo_personalizacion_deteccion()


print("""
✨ EJEMPLOS DE BÚSQUEDA INTELIGENTE CARGADOS ✨

Funciones disponibles:
- ejemplo_busqueda_simple() - Búsqueda básica
- ejemplo_busqueda_detallada() - Análisis completo  
- ejemplo_busqueda_conversacional() - Sistema de chat
- ejemplo_analisis_patrones() - Patrones de aprendizaje
- ejemplo_busquedas_lote() - Búsquedas múltiples
- ejemplo_personalizacion_deteccion() - Detección personalizada

Para ejecutar: nombre_funcion()
Ejemplo: ejemplo_busqueda_simple()
""")
