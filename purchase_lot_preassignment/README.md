# Purchase Lot Preassignment v1.0.0

## Descripción

Módulo para **Odoo 18 Enterprise** que permite crear y pre-asignar números de serie/lotes en pedidos de compra antes de
la recepción del producto. Facilita la coordinación con fabricantes externos para que asignen los lotes deseados y
valida en la recepción que coincidan con lo esperado.

## Características Principales

### 🎯 **Funcionalidades Core**

- **Generación Automática**: Botón "Generate Lots" crea lotes pre-asignados desde el pedido de compra
- **Gestión Completa**: Tabla de lotes por producto y línea de compra con estados (Draft → Confirmed → Received)
- **Validación Inteligente**: Control configurable de lotes en recepción (estricto o suave)
- **Trazabilidad Completa**: Soporte para números de serie (1:1) y lotes (1:N)
- **Compatible Odoo 18**: Sin warnings de deprecación, usa @api.model_create_multi

### 🔧 **Nuevas Funciones v1.0.0**

- **Secuencia Estándar Odoo**: Usa la secuencia nativa `stock.lot.serial` (Serial Numbers)
- **Generación Incremental**: Solo crea lotes faltantes al modificar cantidades en pedidos confirmados
- **Campo "Preassigned Lots"**: Boolean en albaranes para controlar validación
- **Validación Inteligente de Parciales**: Maneja recepciones parciales sin errores de validación
- **Validación Estricta**: Solo acepta lotes pre-asignados cuando está activado
- **Validación Suave**: Permite cualquier lote con warnings cuando está desactivado
- **Auto-Reset de Estados**: Corrige automáticamente lotes marcados prematuramente como recibidos
- **Mensajes Informativos**: Errores detallados con opciones de solución
- **Configuración Nativa**: Numeración configurable desde Configuración → Secuencias

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

#### Generación Incremental (v1.0.0)

- **Pedidos nuevos**: Crea todos los lotes necesarios
- **Modificación de cantidades**: Solo genera los lotes faltantes
- **Respeta lotes existentes**: Conserva lotes ya recibidos o confirmados

```
Ejemplo:
- Pedido original: 3 unidades → 3 lotes creados
- Recibidas: 2 unidades → 2 lotes marcados 'received'
- Modificar a 10 unidades → "Generate Lots" crea solo 7 adicionales
- Resultado: 10 lotes total (3 originales + 7 nuevos)
```

### 3. Validar en Recepción

1. Abrir albarán de recepción
2. Verificar campo **"Preassigned Lots"**:
    - ✅ **Marcado (default)**: Solo acepta lotes pre-asignados
    - ⚪ **Desmarcado**: Acepta cualquier lote (warnings)
3. Proceder con recepción normal

#### Recepciones Parciales (v1.0.0)

- **Validación inteligente**: Solo valida cantidades realmente recibidas (qty_done > 0)
- **Sin errores de "lotes faltantes"**: Permite entregas escalonadas
- **Auto-reset de estados**: Corrige lotes marcados prematuramente como recibidos

```
Ejemplo de recepción parcial:
- Pedido: 10 unidades con 10 números de serie
- Recepción 1: 3 unidades con SN001, SN002, SN003 ✅
- Recepción 2: 4 unidades con SN004-SN007 ✅
- Recepción 3: 3 unidades con SN008-SN010 ✅
```

## Nomenclatura de Lotes/Series

### Secuencia Estándar de Odoo (por defecto)

```
Formato estándar: SN00001, SN00002, SN00003...
Secuencia usada: stock.lot.serial (Serial Numbers)
Configurable desde: Configuración → Técnico → Secuencias
```

### Personalización de Formato

Los administradores pueden configurar el formato desde Odoo:

```
Ejemplos configurables:
- LOT-2025-00001
- SERIE-EMPRESA-00001  
- NS-{YYYY}-{MM}-00001
```

**Configuración:** Configuración → Técnico → Secuencias e Identificadores → Buscar "Serial Numbers"

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
- **Recepciones parciales**: Lotes por fecha de caducidad

### 🔧 **Manufactura de Precisión**

- Coordinación con proveedores
- Control de calidad desde origen
- Trazabilidad proactiva
- **Cantidades variables**: Ajuste de pedidos según demanda

### 📦 **Distribución General**

- Flexibilidad con diferentes proveedores
- Warnings informativos suficientes
- Validación suave según necesidades
- **Entregas escalonadas**: Múltiples recepciones parciales

### 💹 **Gestión de Cantidades Variables (v1.0.0)**

```
Escenario real:
1. Pedido inicial: 50 componentes electrónicos
2. Recepción parcial: 30 unidades procesadas
3. Cambio de demanda: Incrementar a 200 unidades
4. "Generate Lots": Solo crea 150 lotes adicionales
5. Resultado: Continuidad sin duplicados
```

**Beneficios:**
- ⚙️ Adaptación ágil a cambios de demanda
- 📊 Optimización de inventario
- 🔄 Integración perfecta con recepciones parciales
- 🎯 Precisión en control de lotes

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
└── README.md                           # Esta documentación
```

## Personalización

### Configuración de Numeración

El módulo usa la **secuencia estándar de Odoo** `stock.lot.serial`. Para personalizar la numeración:

1. **Ir a:** Configuración → Técnico → Secuencias e Identificadores → Secuencias
2. **Buscar:** "Serial Numbers" o código `stock.lot.serial`
3. **Configurar:** Prefijo, sufijo, padding, etc.

```
Ejemplos de configuración:
- Prefijo: "LOT-", Sufijo: "-2025" → LOT-00001-2025
- Prefijo: "SN", Padding: 6 → SN000001
- Usar fecha: "NS-%(year)s-" → NS-2025-00001
```

**Ventaja:** Sin modificar código, configurable desde interfaz de Odoo.

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
4. **v1.0.0**: El sistema auto-resetea lotes marcados prematuramente

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

### ❌ Error en recepción parcial "Faltan X números de serie"

**Solución automática (v1.0.0)**:

- El sistema solo valida cantidades con `qty_done > 0`
- No requiere números de serie para cantidades no recibidas
- Permite entregas escalonadas sin errores

### ❌ "Generate Lots" crea duplicados al modificar cantidades

**Solución automática (v1.0.0)**:

- Generación incremental: solo crea lotes faltantes
- Conserva lotes existentes (received/confirmed)
- Continúa secuencia desde último número

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

Para soporte técnico:

- Revisar logs de Odoo para debugging
- Verificar permisos de usuario
- Documentación completa incluida en este README

---

**Purchase Lot Preassignment v1.0.0** - Trazabilidad proactiva para compras inteligentes.
