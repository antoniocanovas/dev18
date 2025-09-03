# -*- coding: utf-8 -*-
"""
Script de debug para product_variant_search
Ejecutar desde shell de Odoo para identificar problemas
"""

def debug_variant_search():
    """
    Debug completo de la funcionalidad
    """
    print("=== DEBUG BÚSQUEDA DE VARIANTES ===\n")
    
    # 1. Verificar productos con variantes
    products_with_variants = env['product.product'].search([
        ('product_template_attribute_value_ids', '!=', False),
        ('active', '=', True)
    ], limit=5)
    
    print(f"1. Productos con variantes encontrados: {len(products_with_variants)}")
    
    for product in products_with_variants:
        print(f"\n--- PRODUCTO: {product.display_name} ---")
        print(f"  ID: {product.id}")
        print(f"  Template: {product.product_tmpl_id.name}")
        print(f"  var_desc: '{product.var_desc}'")
        
        # Mostrar atributos individuales
        attrs = product.product_template_attribute_value_ids
        if attrs:
            print(f"  Atributos ({len(attrs)}):")
            for attr in attrs:
                print(f"    - {attr.attribute_id.name}: {attr.product_attribute_value_id.name}")
        
        # Forzar recálculo de var_desc si está vacío
        if not product.var_desc:
            print("  ⚠️ var_desc vacío, forzando recálculo...")
            product._compute_var_desc()
            print(f"  var_desc después de recálculo: '{product.var_desc}'")

def test_manual_search(search_term):
    """
    Prueba manual de búsqueda con logging
    """
    print(f"\n=== PRUEBA MANUAL: '{search_term}' ===")
    
    # Activar logging temporal
    import logging
    logging.getLogger('odoo.addons.product_variant_search.models.product_product').setLevel(logging.INFO)
    
    # Realizar búsqueda
    results = env['product.product'].name_search(search_term)
    
    print(f"\nResultados de búsqueda ({len(results)}):")
    for product_id, display_name in results:
        product = env['product.product'].browse(product_id)
        print(f"  - {display_name}")
        print(f"    var_desc: '{product.var_desc}'")
        
        # Verificar si coincide con nuestros términos
        terms = search_term.lower().split()
        var_desc_lower = (product.var_desc or '').lower()
        matches = all(term in var_desc_lower for term in terms)
        print(f"    Coincide con términos: {'✅' if matches else '❌'}")

def create_test_product():
    """
    Crear producto de prueba con variantes
    """
    print("\n=== CREAR PRODUCTO DE PRUEBA ===")
    
    # Buscar o crear atributos
    color_attr = env['product.attribute'].search([('name', '=', 'Color')], limit=1)
    if not color_attr:
        color_attr = env['product.attribute'].create({
            'name': 'Color',
            'display_type': 'radio',
        })
    
    # Buscar o crear valores de atributo
    red_value = env['product.attribute.value'].search([
        ('attribute_id', '=', color_attr.id),
        ('name', '=', 'Rojo')
    ], limit=1)
    if not red_value:
        red_value = env['product.attribute.value'].create({
            'name': 'Rojo',
            'attribute_id': color_attr.id,
        })
    
    blue_value = env['product.attribute.value'].search([
        ('attribute_id', '=', color_attr.id),
        ('name', '=', 'Azul')
    ], limit=1)
    if not blue_value:
        blue_value = env['product.attribute.value'].create({
            'name': 'Azul',
            'attribute_id': color_attr.id,
        })
    
    # Crear template si no existe
    template_name = 'PRODUCTO1 TEST'
    template = env['product.template'].search([('name', '=', template_name)], limit=1)
    if not template:
        template = env['product.template'].create({
            'name': template_name,
            'type': 'product',
            'attribute_line_ids': [(0, 0, {
                'attribute_id': color_attr.id,
                'value_ids': [(6, 0, [red_value.id, blue_value.id])]
            })]
        })
        print(f"✅ Producto template creado: {template.name}")
    else:
        print(f"✅ Producto template existe: {template.name}")
    
    # Verificar variantes
    variants = template.product_variant_ids
    print(f"Variantes generadas: {len(variants)}")
    for variant in variants:
        print(f"  - {variant.display_name}")
        variant._compute_var_desc()
        print(f"    var_desc: '{variant.var_desc}'")
    
    return template

def full_debug():
    """
    Debug completo paso a paso
    """
    print("🔍 INICIANDO DEBUG COMPLETO\n")
    
    # 1. Verificar productos existentes
    debug_variant_search()
    
    # 2. Crear producto de prueba si es necesario
    test_template = create_test_product()
    
    # 3. Probar búsquedas específicas
    test_searches = [
        'PRODUCTO1 ROJO',
        'ROJO PRODUCTO1', 
        'PRODUCTO1 Azul',
        'Azul TEST'
    ]
    
    for search_term in test_searches:
        test_manual_search(search_term)

# Para ejecutar:
# full_debug()
# debug_variant_search()
# test_manual_search("PRODUCTO1 ROJO")
