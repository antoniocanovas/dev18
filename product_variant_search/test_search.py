# -*- coding: utf-8 -*-
"""
Script de verificación para product_variant_search
Ejecutar desde shell de Odoo para probar el módulo
"""

def test_variant_search():
    """
    Prueba la funcionalidad de búsqueda de variantes
    """
    print("=== PRUEBA DE BÚSQUEDA DE VARIANTES ===")
    
    # Obtener algunos productos con variantes
    products = env['product.product'].search([
        ('product_template_attribute_value_ids', '!=', False)
    ], limit=5)
    
    if not products:
        print("⚠️  No se encontraron productos con variantes para probar")
        return
    
    print(f"✅ Encontrados {len(products)} productos con variantes")
    
    for product in products:
        print(f"\n--- Producto: {product.display_name} ---")
        print(f"    var_desc: {product.var_desc}")
        
        # Probar búsqueda con palabras en diferente orden
        if product.var_desc:
            words = product.var_desc.split()
            if len(words) >= 2:
                # Búsqueda estándar (una palabra)
                single_search = env['product.product'].name_search(words[0])
                found_single = any(item[0] == product.id for item in single_search)
                
                # Buscar con orden original (múltiples palabras)
                search1 = env['product.product'].name_search(' '.join(words[:2]))
                # Buscar con orden invertido (múltiples palabras)
                search2 = env['product.product'].name_search(' '.join(reversed(words[:2])))
                
                found1 = any(item[0] == product.id for item in search1)
                found2 = any(item[0] == product.id for item in search2)
                
                print(f"    🔍 Búsqueda '{words[0]}': {'✅' if found_single else '❌'}")
                print(f"    🔍 Búsqueda '{' '.join(words[:2])}': {'✅' if found1 else '❌'}")
                print(f"    🔍 Búsqueda '{' '.join(reversed(words[:2]))}': {'✅' if found2 else '❌'}")
                
                if found2 and not found_single:
                    print("    ✨ ¡Búsqueda flexible funcionando!")

def test_specific_search(search_term):
    """
    Prueba una búsqueda específica
    """
    print(f"\n=== PRUEBA DE BÚSQUEDA: '{search_term}' ===")
    
    results = env['product.product'].name_search(search_term)
    
    print(f"Encontrados {len(results)} productos:")
    for product_id, display_name in results:
        product = env['product.product'].browse(product_id)
        print(f"  - {display_name}")
        print(f"    var_desc: {product.var_desc}")

# Para ejecutar desde shell de Odoo:
# test_variant_search()
# test_specific_search("Azul L")
