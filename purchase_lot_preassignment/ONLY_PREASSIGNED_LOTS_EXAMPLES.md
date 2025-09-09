# Campo "Preassigned Lots" - Ejemplos de Uso

## Descripción del Campo

El campo **"Preassigned Lots"** es un boolean que aparece en los albaranes de recepción (recepciones de compra) y controla el nivel de validación de lotes/números de serie recibidos.

- **Valor por defecto**: `True`
- **Ubicación**: Albarán de recepción, antes de la lista de movimientos
- **Visible**: Solo en recepciones de compra con pedido asociado

## Comportamiento del Campo

### ✅ `only_preassigned_lots = True` (Por defecto)
**Validación ESTRICTA**: Solo permite lotes que estén en la lista de preasignados.

### 📝 `only_preassigned_lots = False`  
**Validación SUAVE**: Permite cualquier lote, solo muestra warnings.

---

## Ejemplo 1: Validación Estricta (Campo = True)

### Escenario
- Pedido de compra: 10 microcontroladores ESP32
- Lotes preasignados: `ESP32-PO001-SN0001`, `ESP32-PO001-SN0002`, `ESP32-PO001-SN0003`
- `only_preassigned_lots = True`

### Caso A: Recepción Correcta ✅
**Lotes recibidos**: `ESP32-PO001-SN0001`, `ESP32-PO001-SN0002`

**Resultado**: 
- ✅ Validación exitosa
- ✅ Albarán se valida sin problemas
- ✅ Lotes marcados como recibidos

### Caso B: Recepción con Lotes No Preasignados ❌
**Lotes recibidos**: `ESP32-PO001-SN0001`, `ESP32-CUSTOM-001`

**Resultado**:
```
❌ ValidationError: 
The following lot/serial numbers are not in the preassigned list for product ESP32-WROOM: ESP32-CUSTOM-001

Expected lots: ESP32-PO001-SN0001, ESP32-PO001-SN0002, ESP32-PO001-SN0003

To receive these lots, either:
- Disable "Preassigned Lots" option
- Add these lots to the preassigned list in the purchase order
```

### Caso C: Producto Sin Lotes Preasignados ❌
**Lotes recibidos**: `RANDOM-LOT-001`
**Lotes preasignados**: Ninguno

**Resultado**:
```
❌ ValidationError:
Product ESP32-WROOM has no preassigned lots, but lot/serial numbers were provided. 
Either disable "Preassigned Lots" or create preassigned lots first.
```

---

## Ejemplo 2: Validación Suave (Campo = False)

### Escenario
- Mismo pedido de compra
- `only_preassigned_lots = False`

### Caso: Recepción con Lotes No Preasignados 📝
**Lotes recibidos**: `ESP32-PO001-SN0001`, `ESP32-CUSTOM-001`

**Resultado**:
- ✅ Validación exitosa (no se bloquea)
- 📝 Warning en chatter del albarán:
```
Lot validation warnings for product ESP32-WROOM:
Unexpected lots received: ESP32-CUSTOM-001
```

---

## Flujo de Trabajo Recomendado

### 1. Configuración Inicial
```
Pedido de Compra: PO001
Producto: ESP32-WROOM (tracking: serial)
Cantidad: 5 unidades
Estado: purchase (confirmado)
```

### 2. Generar Lotes Preasignados
- Hacer clic en **"Generate Lots"** en el pedido
- Se crean automáticamente:
  - `ESP32-PO001-SN0001`
  - `ESP32-PO001-SN0002`  
  - `ESP32-PO001-SN0003`
  - `ESP32-PO001-SN0004`
  - `ESP32-PO001-SN0005`

### 3. Comunicar al Proveedor
Enviar lista de números de serie esperados al proveedor para que los asigne correctamente.

### 4. Recepción de Mercancía
**Albarán automático con**:
- `only_preassigned_lots = True` ✅
- Campo visible y editable

### 5. Validación Durante Recepción

#### Opción A: Validación Estricta (Recomendado)
- Mantener `only_preassigned_lots = True`
- Solo aceptar lotes preasignados
- Control total de trazabilidad

#### Opción B: Validación Flexible
- Cambiar a `only_preassigned_lots = False`
- Aceptar cualquier lote
- Solo recibir warnings informativos

---

## Casos de Uso Empresariales

### 🏥 Industria Farmacéutica
**Recomendación**: `only_preassigned_lots = True`
- Control estricto de lotes por regulaciones
- Trazabilidad completa obligatoria
- Prevención de errores críticos

### 🔧 Manufactura General  
**Recomendación**: `only_preassigned_lots = True`
- Control de calidad mejorado
- Coordinación con proveedores
- Trazabilidad proactiva

### 📦 Distribución Flexible
**Recomendación**: `only_preassigned_lots = False`  
- Acepta lotes variables de proveedores
- Flexibilidad operativa
- Warnings informativos suficientes

---

## Solución de Problemas

### Error: "Lot not in preassigned list"
**Soluciones**:
1. **Desactivar validación**: Cambiar `only_preassigned_lots = False`
2. **Añadir lote**: Ir al pedido → "View Lots" → Crear lote manualmente
3. **Regenerar lotes**: En pedido → "Generate Lots" (elimina drafts y recrea)

### Error: "No preassigned lots found"
**Soluciones**:
1. **Crear lotes**: Ir al pedido → "Generate Lots"
2. **Desactivar validación**: Cambiar `only_preassigned_lots = False`
3. **Verificar tracking**: Confirmar que producto tiene trazabilidad lot/serial

### Campo No Visible
**Verificar**:
- Albarán es de tipo "incoming" (recepción)
- Tiene pedido de compra asociado
- Productos tienen trazabilidad configurada

---

## Beneficios del Campo

### ✅ Control Granular
- Activar/desactivar validación según necesidades
- Flexibilidad por albarán individual
- Adaptable a diferentes proveedores

### ✅ Experiencia de Usuario Mejorada
- Mensajes de error claros y explicativos
- Opciones de solución integradas  
- No bloquea cuando no es necesario

### ✅ Trazabilidad Proactiva
- Coordinación con proveedores mejorada
- Control de calidad desde origen
- Prevención de errores en recepción

El campo **"Preassigned Lots"** proporciona el equilibrio perfecto entre control estricto y flexibilidad operativa.
