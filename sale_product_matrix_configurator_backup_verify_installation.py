# -*- coding: utf-8 -*-
"""
Script de verificación para el módulo Sale Product Matrix Configurator
Ejecutar desde shell de Odoo:

exec(open('/path/to/sale_product_matrix_configurator/verify_installation.py').read())
"""

def verify_installation():
    """Verificar instalación y funcionamiento del módulo"""
    
    print("🔍 === VERIFICACIÓN: Sale Product Matrix Configurator ===")
    
    # 1. Verificar que el módulo está instalado
    try:
        module = env['ir.module.module'].search([
            ('name', '=', 'sale_product_matrix_configurator'),
            ('state', '=', 'installed')
        ])
        if module:
            print(f"✅ Módulo instalado correctamente - Versión: {module.latest_version}")
        else:
            print("❌ Módulo no está instalado")
            return False
    except Exception as e:
        print(f"❌ Error verificando módulo: {e}")
        return False
    
    # 2. Verificar campos del modelo
    try:
        # Verificar campo configurator_mode
        line_model = env['sale.order.line']
        if 'configurator_mode' in line_model._fields:
            print("✅ Campo 'configurator_mode' encontrado en sale.order.line")
        else:
            print("❌ Campo 'configurator_mode' no encontrado")
        
        # Verificar campo product_custom_attribute_value_ids
        if 'product_custom_attribute_value_ids' in line_model._fields:
            field = line_model._fields['product_custom_attribute_value_ids']
            if hasattr(field, 'inverse_name') and field.inverse_name == 'sale_order_line_id':
                print("✅ Campo 'product_custom_attribute_value_ids' configurado correctamente")
            else:
                print("❌ Campo 'product_custom_attribute_value_ids' mal configurado")
        
    except Exception as e:
        print(f"❌ Error verificando campos: {e}")
    
    # 3. Verificar campo sale_order_line_id
    try:
        custom_model = env['product.attribute.custom.value']
        if 'sale_order_line_id' in custom_model._fields:
            print("✅ Campo 'sale_order_line_id' encontrado en product.attribute.custom.value")
        else:
            print("❌ Campo 'sale_order_line_id' no encontrado")
    except Exception as e:
        print(f"❌ Error verificando sale_order_line_id: {e}")
    
    # 4. Test básico de funcionamiento
    try:
        print("\n🧪 === TEST BÁSICO ===")
        
        # Crear partner, orden y producto de test
        partner = env['res.partner'].create({'name': 'Test Partner Verification'})
        order = env['sale.order'].create({'partner_id': partner.id})
        
        # Crear atributo de texto
        attribute = env['product.attribute'].create({
            'name': 'Test Text Attribute',
            'display_type': 'text',
        })
        
        # Crear template de producto
        template = env['product.template'].create({
            'name': 'Test Product for Verification',
            'type': 'consu',
        })
        
        # Crear línea attribute
        attr_line = env['product.template.attribute.line'].create({
            'product_tmpl_id': template.id,
            'attribute_id': attribute.id,
            'value_ids': [(0, 0, {
                'name': 'Custom Text Value',
                'attribute_id': attribute.id,
                'is_custom': True,
            })],
        })
        
        # Crear línea de venta
        line = env['sale.order.line'].create({
            'order_id': order.id,
            'product_template_id': template.id,
            'configurator_mode': 'configurator',
            'product_uom_qty': 1,
        })
        
        print(f"✅ Línea de venta creada - ID: {line.id}")
        print(f"✅ Configurator mode: {line.configurator_mode}")
        
        # Test custom attribute value
        ptav = attr_line.value_ids[0]
        custom_val = env['product.attribute.custom.value'].create({
            'custom_product_template_attribute_value_id': ptav.id,
            'custom_value': 'Mi texto personalizado de prueba',
            'sale_order_line_id': line.id,
        })
        
        print(f"✅ Custom attribute value creado - ID: {custom_val.id}")
        print(f"✅ Valor: '{custom_val.custom_value}'")
        print(f"✅ Nombre calculado: '{custom_val.name}'")
        
        # Verificar relación
        line_customs = line.product_custom_attribute_value_ids
        if custom_val in line_customs:
            print("✅ Relación One2many funciona correctamente")
        else:
            print("❌ Relación One2many no funciona")
        
        # Limpiar test data
        order.unlink()
        template.unlink()
        attribute.unlink()
        partner.unlink()
        
        print("✅ Test básico completado exitosamente")
        
    except Exception as e:
        print(f"❌ Error en test básico: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Verificar líneas existentes con custom attributes
    try:
        print("\n📊 === ESTADÍSTICAS ACTUALES ===")
        
        lines_with_custom = env['sale.order.line'].search([
            ('product_custom_attribute_value_ids', '!=', False)
        ])
        print(f"📈 Líneas de venta con custom attributes: {len(lines_with_custom)}")
        
        if lines_with_custom:
            recent_line = lines_with_custom[0]
            print(f"📋 Ejemplo - Línea ID: {recent_line.id}")
            print(f"📋 Producto: {recent_line.product_id.name if recent_line.product_id else 'Sin producto'}")
            print(f"📋 Custom attributes: {len(recent_line.product_custom_attribute_value_ids)}")
            
            for custom in recent_line.product_custom_attribute_value_ids[:3]:  # Solo los primeros 3
                print(f"   - {custom.name}")
        
        total_custom_attrs = env['product.attribute.custom.value'].search_count([])
        print(f"📈 Total custom attribute values en sistema: {total_custom_attrs}")
        
    except Exception as e:
        print(f"❌ Error obteniendo estadísticas: {e}")
    
    print("\n✅ === VERIFICACIÓN COMPLETADA ===")
    print("💡 Si todos los elementos muestran ✅, el módulo está funcionando correctamente")
    return True

# Ejecutar verificación
if 'env' in globals():
    verify_installation()
else:
    print("❌ Este script debe ejecutarse desde shell de Odoo donde 'env' esté disponible")
    print("💡 Ejecutar: ./odoo-bin shell -d tu_database")
    print("💡 Luego: exec(open('verify_installation.py').read())")
