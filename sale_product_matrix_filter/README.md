# Sale Product Matrix Filter v18.0.1.0.4

Este módulo extiende la funcionalidad de matriz de productos de Odoo 18 Enterprise para permitir filtrar la matriz por valores específicos de atributos.

## Características

- **Campo de filtro**: Agrega un campo `value_filter_id` en las órdenes de venta para seleccionar un valor de atributo específico
- **Filtrado de matriz**: La matriz de productos muestra solo las variantes que contengan el atributo seleccionado
- **Compatibilidad**: Mantiene toda la funcionalidad existente de la matriz de productos
- **Interfaz amigable**: Campo visible en el formulario de orden de venta

## Historial de Cambios

### v18.0.1.0.4 (Actual)
- **OPTIMIZADO**: Código JavaScript consolidado y más eficiente
- **MEJORADO**: Separación de responsabilidades en métodos privados
- **MEJORADO**: Mejor manejo de errores con logging específico
- **MEJORADO**: Código más legible y mantenible

### v18.0.1.0.3
- **CORREGIDO**: Error JavaScript cuando la matriz filtrada está vacía
- **AÑADIDO**: ValidationError para matrices sin variantes coincidentes
- **MEJORADO**: Doble estrategia de prevención de errores

### v18.0.1.0.2
- **CORREGIDO**: Error JavaScript cuando matriz filtrada está vacía
- **MEJORADO**: Manejo de matrices vacías sin errores en el frontend

### v18.0.1.0.1
- **CORREGIDO**: Error KeyError: 'attribute_value_id' 
- **MEJORADO**: Ahora usa correctamente 'product_attribute_value_id'

### v18.0.1.0.0
- Versión inicial con funcionalidad básica de filtrado

## Instalación

1. Copia el módulo a tu directorio de addons de Odoo
2. Actualiza la lista de aplicaciones
3. Instala el módulo "Sale Product Matrix Filter"

## Uso

1. Abre una orden de venta
2. Ve a la pestaña "Other Info"
3. En la sección "Sales", selecciona un valor de atributo en el campo "Filtro de Variante"
4. Al abrir el configurador de matriz de productos, solo se mostrarán las variantes que contengan el atributo seleccionado

## Ejemplo

Si tienes un producto con atributos de Color (Rojo, Azul) y Talla (S, M, L), y seleccionas "Talla: L" como filtro:
- La matriz solo mostrará las combinaciones que incluyan la talla L
- Se mantendrán las cantidades y precios correctos
- El resto de la funcionalidad permanece intacta

## Arquitectura Técnica

### Backend (Python)
- **Prevención**: Evita matrices vacías con ValidationError
- **Filtrado**: Lógica eficiente de filtrado de variantes
- **Validación**: Verificación de variantes coincidentes

### Frontend (JavaScript)
- **Modular**: Código dividido en métodos privados especializados
- **Robusto**: Manejo de errores con try-catch
- **Eficiente**: Optimización del rendimiento
- **Mantenible**: Código autodocumentado

## Compatibilidad

- Odoo 18.0 Enterprise
- Módulos requeridos: `sale`, `sale_product_matrix`, `product`

## Archivos Técnicos

- `models/sale_order.py`: Lógica de filtrado con ValidationError
- `views/sale_order_views.xml`: Campo de filtro en el formulario
- `static/src/js/product_matrix_dialog_patch.js`: Patch JavaScript optimizado

## Soporte

Para reportar bugs o solicitar nuevas funcionalidades, contacta a:
**Antonio Canovas Pedreno**

## Licencia

LGPL-3
