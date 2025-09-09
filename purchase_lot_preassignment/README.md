# Purchase Lot Preassignment v1.0.0

## Descripción

Módulo para **Odoo 18 Enterprise** que permite crear y pre-asignar números de serie/lotes en pedidos de compra antes de la recepción del producto. Facilita la coordinación con fabricantes externos para que asignen los lotes deseados y valida en la recepción que coincidan con lo esperado.

## Características Principales

### 🎯 **Funcionalidades Core**
- **Generación Automática**: Botón "Generate Lots" crea lotes pre-asignados desde el pedido de compra
- **Gestión Completa**: Tabla de lotes por producto y línea de compra con estados (Draft → Confirmed → Received)
- **Validación Inteligente**: Control configurable de lotes en recepción (estricto o suave)
- **Trazabilidad Completa**: Soporte para números de serie (1:1) y lotes (1:N)
- **Compatible Odoo 18**: Sin warnings de deprecación, usa @api.model_create_multi

### 🔧 **Nuevas Funciones v1.0.0**
- **Campo "Preassigned Lots"**: Boolean en albaranes para controlar validación
- **Validación Estricta**: Solo acepta lotes pre-asignados cuando está activado
- **Validación Suave**: Permite cualquier lote con warnings cuando está desactivado
- **Mensajes Informativos**: Errores detallados con opciones de solución

## Instalación

### Requisitos
- **Odoo 18 Enterprise**
- Módulos base: `purchase`, `stock`, `purchase_stock`

### Pasos de Instalación

1. **Copiar módulo al directorio de addons**:
   ```bash
   cp -r purchase_lot_preassignment /path/to/your/addons/
   ```

2. **Actualizar lista de aplicaciones** en Odoo:
   ```
   Aplicaciones > Actualizar Lista de Aplicaciones
   ```

3. **Instalar módulo**:
   ```
   Buscar "Purchase Lot Preassignment" > Instalar
   ```

4. **Comando desde terminal** (opcional):
   ```bash
   cd /path/to/odoo18
   python3 odoo-bin -d DATABASE -i purchase_lot_preassignment --addons-path=/path/to/addons
   ```

## Uso Rápido

### 1. Configurar Productos
Asegurar que los productos tengan **trazabilidad configurada**:
- Ir a producto → pestaña **Inventario**
- **Tracking**: Seleccionar "By Lots" o "By Unique Serial Number"

### 2. Crear Lotes Pre-asignados
1. Crear pedido de compra con productos que tengan trazabilidad
2. **Confirmar pedido** (estado = 'purchase')
3. Hacer clic en **"Generate Lots"**
4. El sistema crea automáticamente lotes/números de serie

### 3. Validar en Recepción
1. Abrir albarán de recepción
2. Verificar campo **"Preassigned Lots"**:
   - ✅ **Marcado (default)**: Solo acepta lotes pre-asignados
   - ⚪ **Desmarcado**: Acepta cualquier lote (warnings)
3. Proceder con recepción normal

## Ejemplos de Nomenclatura

### Números de Serie
```
Producto: ESP32-WROOM
Pedido: PO0001
Generados: ESP32-PO0001-SN0001, ESP32-PO0001-SN0002, ESP32-PO0001-SN0003...
```

### Lotes
```
Producto: ANTIBIOTIC-500MG  
Pedido: PO0123
Generados: ANTIBIOTIC-PO0123-L001, ANTIBIOTIC-PO0123-L002, ANTIBIOTIC-PO0123-L003...
```

## Flujo de Trabajo Completo

### Fase 1: Preparación
1. **Crear pedido** con productos trazables
2. **Confirmar pedido** (botón "Generate Lots" aparece)
3. **Generar lotes** automáticamente
4. **Comunicar lista** al proveedor

### Fase 2: Recepción
1. **Albarán automático** con "Preassigned Lots" = True
2. **Recibir productos** con lotes específicos
3. **Validación automática**:
   - ✅ Lotes coinciden → Continúa
   - ❌ Lotes no coinciden → Error informativo

### Fase 3: Resolución de Conflictos
Si hay lotes no esperados:
1. **Opción A**: Desmarcar "Preassigned Lots" (acepta cualquier lote)
2. **Opción B**: Ir al pedido → "View Lots" → Añadir lotes manualmente
3. **Opción C**: Regenerar lotes desde pedido

## Validación de Lotes

### 🔒 Validación Estricta (Preassigned Lots = ✅)
- **Solo acepta** lotes de la lista pre-asignada
- **Bloquea validación** si hay lotes no esperados
- **Error detallado** con opciones de solución
- **Ideal para**: Industrias reguladas, control de calidad estricto

### 📝 Validación Suave (Preassigned Lots = ⚪)
- **Acepta cualquier lote** o número de serie
- **Warnings en chatter** para lotes inesperados
- **No bloquea** la validación
- **Ideal para**: Distribución flexible, proveedores variables

## Casos de Uso Empresariales

### 🏥 **Industria Farmacéutica**
- Control estricto por regulaciones
- Trazabilidad completa obligatoria
- Validación estricta recomendada

### 🔧 **Manufactura de Precisión**
- Coordinación con proveedores
- Control de calidad desde origen
- Trazabilidad proactiva

### 📦 **Distribución General**
- Flexibilidad con diferentes proveedores
- Warnings informativos suficientes
- Validación suave según necesidades

## Estructura del Módulo

```
purchase_lot_preassignment/
├── __manifest__.py                     # Configuración v1.0.0
├── __init__.py                         # Importaciones
├── models/
│   ├── __init__.py
│   ├── purchase_lot_preassignment.py  # Modelo principal
│   ├── purchase_order.py              # Extensión pedidos
│   └── stock_picking.py               # Extensión recepciones
├── views/
│   ├── purchase_order_views.xml       # Botón + vistas pedidos
│   ├── purchase_lot_preassignment_views.xml # Gestión lotes
│   └── stock_picking_views.xml        # Campo validación
├── security/
│   └── ir.model.access.csv            # Permisos
├── README.md                           # Esta documentación
└── ONLY_PREASSIGNED_LOTS_EXAMPLES.md # Ejemplos detallados
```

## Personalización

### Nomenclatura de Lotes
Modificar `_generate_lot_name()` en `models/purchase_order.py`:
```python
def _generate_lot_name(self, line, sequence):
    # Personalizar formato aquí
    product_code = line.product_id.default_code or 'PROD'
    return f"CUSTOM-{product_code}-{sequence:05d}"
```

### Tamaño de Lotes
Personalizar `_get_lot_size()` para usar configuración del producto:
```python
def _get_lot_size(self, line):
    return line.product_id.lot_size or 100.0
```

## Solución de Problemas

### ❌ "Lot not in preassigned list"
**Soluciones**:
1. Desmarcar "Preassigned Lots" en albarán
2. Ir al pedido → "View Lots" → Añadir lote manualmente
3. Regenerar lotes: Pedido → "Generate Lots"

### ❌ "No preassigned lots found"
**Verificar**:
1. Producto tiene trazabilidad (lot/serial) configurada
2. Pedido está confirmado (estado 'purchase')
3. Ejecutar "Generate Lots" desde pedido

### ❌ Campo "Preassigned Lots" no visible
**Verificar**:
1. Albarán es de tipo "incoming" (recepción)
2. Tiene pedido de compra asociado
3. Actualizar módulo si es necesario

## Menús y Navegación

- **Compras → Gestión → Lot Preassignments**: Vista general de todos los lotes
- **Pedidos de Compra**: Botón "Generate Lots" + Smart button contador
- **Albaranes**: Campo "Preassigned Lots" + botón "Expected Lots"

## Compatibilidad

- ✅ **Odoo 18.0 Enterprise**
- ✅ **Módulos estándar**: purchase, stock, purchase_stock
- ✅ **Otros módulos**: Compatible con extensiones de compras/inventario
- ✅ **Base de datos**: Migración automática al instalar

## Licencia

Este módulo está bajo **licencia LGPL-3**.

## Soporte

Para documentación detallada y ejemplos específicos, consultar:
- `ONLY_PREASSIGNED_LOTS_EXAMPLES.md` - Casos de uso detallados
- Logs de Odoo para debugging
- Verificar permisos de usuario

---

**Purchase Lot Preassignment v1.0.0** - Trazabilidad proactiva para compras inteligentes.
