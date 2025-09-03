# Product Variant Search

Módulo para Odoo 18 que permite búsqueda flexible de variantes de producto.

## Funcionalidad

- **Búsqueda independiente del orden**: Busca "Azul L Camiseta" o "Camiseta L Azul" y encuentra el mismo producto
- **Campo calculado optimizado**: `var_desc` almacena nombre + atributos para búsquedas rápidas
- **Doble implementación**: Métodos `name_search` y `_name_search` para máxima compatibilidad
- **Compatibilidad total**: Mantiene la funcionalidad de búsqueda estándar de Odoo

## Ejemplos de uso en líneas de venta

```
"Camiseta Azul L" → encuentra "Camiseta" con atributos "Azul" y "L"
"L Azul"          → encuentra todas las camisetas talla L color Azul  
"Nike Running"    → encuentra productos Nike con "Running" en nombre o atributos
"Rojo XL"         → encuentra productos con atributos "Rojo" y "XL"
```

## Instalación

1. Reiniciar Odoo (para cargar el nuevo módulo)
2. Ir a Aplicaciones → Actualizar lista de aplicaciones
3. Buscar "Product Variant Search" e instalar
4. Los productos existentes calculan automáticamente el campo `var_desc`

## Cómo funciona

1. **Respeta Odoo 18**: Ejecuta primero la búsqueda estándar sofisticada de Odoo 18
2. **Búsqueda adicional**: Si hay múltiples términos y pocos resultados, busca en `var_desc`
3. **Campo optimizado**: `var_desc` se calcula automáticamente: "Camiseta Azul L"
4. **Sin duplicados**: Evita mostrar el mismo producto dos veces
5. **Robusto**: Si algo falla, siempre retorna los resultados estándar

## Pruebas

**Desde shell de Odoo** (Apps → Configuración Técnica → Shell de base de datos):
```python
# Cargar el script de prueba
exec(open('/ruta/a/dev18/product_variant_search/test_search.py').read())

# Probar con productos existentes
test_variant_search()

# Probar búsqueda específica
test_specific_search("Azul L")
```

## Soporte

Compatible con Odoo 18.0
