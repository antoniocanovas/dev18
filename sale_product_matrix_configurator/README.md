# Sale Product Matrix Configurator

Este módulo extiende la funcionalidad de `sale_product_matrix` para permitir alternar entre el modo matriz y el modo configurador de productos en las líneas de pedido de venta.

## Características

- **Campo de selección de modo**: Cada línea de pedido tiene un campo `configurator_mode` que permite elegir entre "Matrix Grid" y "Product Configurator"
- **Detección automática**: El modo se establece automáticamente según la configuración del producto
- **Botón configurador**: Aparece un botón para abrir el configurador cuando el modo está establecido en "configurator"
- **Compatibilidad total**: Mantiene toda la funcionalidad existente del módulo `sale_product_matrix`

## Uso

### En líneas de pedido de venta:

1. **Seleccionar producto**: Al seleccionar un producto con atributos, el campo `configurator_mode` aparecerá
2. **Cambiar modo**: Puedes alternar entre:
   - **Matrix Grid**: Usa la interfaz de matriz tradicional
   - **Product Configurator**: Usa el diálogo paso a paso del configurador
3. **Configurar producto**: 
   - En modo Matrix: Se mostrará la grilla si el producto la soporta
   - En modo Configurator: Aparecerá un botón "Configure Product" que abre el diálogo

### Comportamiento automático:

- Los productos configurados como "matrix" establecerán automáticamente el modo "Matrix Grid"
- Los productos configurados como "configurator" establecerán automáticamente el modo "Product Configurator"
- El usuario puede cambiar manualmente el modo según sus preferencias

## Instalación

1. Copiar el módulo a la carpeta de addons
2. Actualizar lista de aplicaciones
3. Instalar el módulo "Sale Product Matrix Configurator"

## Dependencias

- `sale`
- `sale_product_matrix`
- `product_matrix`

## Compatibilidad

- Odoo 18.0
- Compatible con todos los módulos que extienden `sale_product_matrix`

## Notas técnicas

- El campo `configurator_mode` es editable solo en estado 'draft' y 'sent'
- La funcionalidad JavaScript extiende `SaleOrderLineProductField` sin romper la compatibilidad
- Se mantiene toda la lógica de exclusiones y validaciones de atributos

## Autor

Antonio Canovas Pedreno
