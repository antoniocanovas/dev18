# Purchase Product Matrix Configurator

Módulo para mostrar preferencias de configuración y gestionar valores variables en órdenes de compra.

## Características

- **Campo de preferencia**: Muestra opciones Matrix Grid y Product Configurator (Matrix)
- **Consistencia con ventas**: Interfaz similar al módulo de ventas
- **Compatibilidad**: Funciona con el módulo purchase_product_matrix
- **Valores variables**: Permite añadir costos/valores variables por línea
- **Cálculos automáticos**: Total con variables incluidas
- **Realidad técnica**: Las compras en Odoo solo soportan Matrix Grid

## Nuevos campos de valor variable

### **Campos disponibles**:
- `variable_value`: Valor variable por línea
- `variable_percentage`: Porcentaje variable aplicado
- `variable_cost`: Costo variable por unidad
- `price_total_with_variable`: Total incluyendo valores variables (calculado)

### **Ubicación en vistas**:
- **Formulario orden**: Columnas opcionales después del precio
- **Lista líneas**: Columnas opcionales "Variable" y "Total+Var"
- **Form línea**: Grupo "Variable Values" con todos los campos

## Uso

### **Configuración básica**:
1. Crear nueva línea de orden de compra
2. Seleccionar preferencia de configuración
3. Elegir producto - se abrirá Matrix Grid

### **Valores variables**:
1. En la línea, añadir valores en campos variable
2. El total con variables se calcula automáticamente
3. Los campos aparecen solo cuando tienen valor > 0

## Ejemplos de uso

```python
# Ejemplo: Línea con costo variable
line_vals = {
    'product_id': product.id,
    'product_qty': 10,
    'price_unit': 100.0,
    'variable_value': 5.0,  # €5 extra por línea
    'variable_cost': 2.0,   # €2 extra por unidad
}
# Total normal: 10 × 100 = €1000
# Total con variable: €1000 + (5 × 10) + (2 × 10) = €1070
```

## Nota importante

A diferencia de las ventas, **las compras en Odoo solo soportan Matrix Grid**. Este módulo mantiene consistencia visual pero siempre usa Matrix Grid.

## Instalación

1. Copiar módulo a addons
2. Actualizar lista de aplicaciones
3. Instalar "Purchase Product Matrix Configurator"

## Dependencias

- `purchase`: Módulo base de compras
- `purchase_product_matrix`: Matrix Grid para compras
- `product`: Gestión de productos

## Autor

Antonio Canovas Pedreno
