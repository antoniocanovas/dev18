# shoes_packinglist — Diseño técnico

**Fecha:** 2026-04-24  
**Módulo:** `shoes_packinglist`  
**Autor:** Antonio Cánovas  

---

## Objetivo

Nuevo módulo Odoo 18 para gestionar la importación de packing lists por contenedor.
Permite importar líneas de packing list desde hoja de cálculo, validarlas, detectar los
albaranes implicados, dividirlos si son parciales, y actualizar los datos logísticos
del contenedor (peso bruto, volumen, número de bultos).

El módulo **no modifica** `purchase_container`; solo hereda sus modelos y extiende sus vistas.

---

## Dependencias

- `purchase_container` (OCA) — proporciona `purchase.container` y `stock.picking.container_id`
- `stock` — albaranes y lotes
- `purchase_stock` — transitividad a través de `purchase_container`

---

## Estructura de ficheros

```
shoes_packinglist/
├── __manifest__.py
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── purchase_container_line.py   # nuevo modelo principal
│   └── purchase_container.py        # hereda purchase.container
├── wizard/
│   ├── __init__.py
│   └── packing_list_warning_wizard.py
├── views/
│   ├── purchase_container_line_views.xml
│   ├── purchase_container_views.xml   # xpath sobre vista existente
│   └── packing_list_warning_wizard_views.xml
└── security/
    └── ir.model.access.csv
```

---

## Modelos

### `purchase.container.line`

Representa una línea del packing list importado. Es el modelo central del módulo.

| Campo | Tipo | Digits / Notas |
|---|---|---|
| `container_id` | Many2one `purchase.container` | required, ondelete=cascade, index |
| `shoes_campaign` | Char | informativo |
| `name` | Char | referencia producto (informativo) |
| `color` | Char | informativo |
| `pairs` | Float | `Product Unit of Measure` — informativo |
| `purchase_order` | Char | informativo |
| `assortment` | Char | informativo |
| `lot` | Char | **clave de matching** con `stock.lot.name` |
| `volume` | Float | `Volume` |
| `pair_net_weight` | Float | `Stock Weight` |
| `pair_gross_weight` | Float | `Stock Weight` |
| `assortment_net_weight` | Float | `Stock Weight` |
| `assortment_gross_weight` | Float | `Stock Weight` |
| `shippingmark` | Char | informativo |
| `high` | Float | `Volume` |
| `width` | Float | `Volume` |
| `length` | Float | `Volume` |
| `move_id` | Many2one `stock.move` | enlace al movimiento matcheado; False = sin match |

**Limpieza de datos:** override de `create` y `write` que aplica `.strip()` a todos los
campos Char antes de guardar, eliminando espacios iniciales/finales y tabulaciones.

### `purchase.container` (herencia)

Campos añadidos:
- `container_line_ids` — One2many → `purchase.container.line.container_id`

Métodos añadidos:
- `action_update_from_packing_list()` — lógica completa del botón Update (ver sección flujo)

---

## Flujo del botón "Update"

El método se ejecuta en una sola transacción. Si el wizard de advertencia interviene, la
parte de splitting/asignación se ejecuta solo tras confirmación del usuario (context flag).

### 1. Validación previa
- `shipping_agent_id` no definido → `UserError`
- `container_line_ids` vacío → `UserError`

### 2. Obtener albaranes pendientes del proveedor
```
stock.picking:
  partner_id = shipping_agent_id
  picking_type_id.code = 'incoming'
  state in ('assigned', 'waiting', 'confirmed', 'partially_available')
```
Si no hay resultados → `UserError` con mensaje indicando el proveedor.

### 3. Matching de lotes
Por cada línea del packing list:
- Buscar `stock.lot` donde `name = line.lot` (compañía actual).
- Si existe, buscar `stock.move.line` dentro de los albaranes pendientes con ese `lot_id`.
- Si se encuentra → escribir `move_id` = `stock.move.line.move_id` en la línea.
- Si no se encuentra → añadir al listado de líneas sin match.

El matching no valida el campo `name` (producto), `assortment`, `shippingmark` ni `pairs`:
son informativos. El producto real se obtiene del lote.

### 4. Wizard si hay líneas sin match
Si `unmatched_lines` no está vacío → abrir `packing_list.warning.wizard` con:
- Listado de líneas sin match (lot, name, purchase_order).
- Opción **Continuar** (procesa solo las líneas con `move_id`) o **Cancelar** (no hace nada).

Las líneas sin match mantienen `move_id = False` en cualquier caso, permitiendo filtrarlas
en la vista.

### 5. División y asignación de albaranes
Se trabaja con las líneas que tienen `move_id` asignado.

Para cada `picking` involucrado:
- Calcular `matched_move_lines` = move_lines del picking cuyo `lot_id` está en los lotes matcheados.
- Calcular `remaining_move_lines` = move_lines del picking **no** incluidas.

**Si `remaining_move_lines` está vacío** (picking completo):
```python
picking.container_id = self.id
```

**Si `remaining_move_lines` no está vacío** (picking parcial):
1. Crear picking backorder:
   ```python
   backorder = picking.copy(default={
       'move_ids': [],
       'move_line_ids': [],
       'backorder_id': picking.id,
   })
   ```
2. Para cada `stock.move` con move_lines en ambos grupos:
   - Crear un nuevo `stock.move` en el backorder con `product_uom_qty` = suma de las quantities de las move_lines sobrantes.
   - Reasignar las `stock.move.line` sobrantes al nuevo move y al backorder.
3. Para cada `stock.move` cuyas move_lines van íntegramente al backorder:
   - Reasignar el move completo al backorder.
4. Asignar `container_id = self.id` al picking original (que ahora solo contiene los lotes del packing list).

### 6. Actualizar métricas del contenedor
```python
processed_lines = container_line_ids.filtered('move_id')
self.weight = sum(processed_lines.mapped('assortment_gross_weight'))
self.volume = sum(processed_lines.mapped('volume'))
self.package_qty = len(processed_lines)
```

---

## Wizard `packing_list.warning.wizard`

| Campo | Tipo | Notas |
|---|---|---|
| `container_id` | Many2one `purchase.container` | readonly |
| `warning_line_ids` | One2many `packing.list.warning.line` | líneas sin match |

### `packing.list.warning.line` (transient)

| Campo | Tipo |
|---|---|
| `wizard_id` | Many2one `packing_list.warning.wizard` |
| `lot` | Char |
| `name` | Char |
| `purchase_order` | Char |

**Acciones:**
- `action_continue` → ejecuta el paso 5 y 6 pasando `skip_unmatched=True` en context.
- `action_cancel` → cierra sin hacer nada.

---

## Vistas

### Extensión de `purchase.container` (xpath)

1. **Botón "Update"** en `<header>`, invisible cuando `state == 'locked'`.
2. **Página "Packing List"** en el notebook (o grupo si no hay notebook):
   - Lista editable inline de `container_line_ids`.
   - Columnas principales: `lot`, `name`, `color`, `assortment`, `pairs`, `purchase_order`, `shippingmark`, `assortment_gross_weight`, `volume`, `move_id` (readonly).
   - Columnas opcionales (optional="hide"): `pair_net_weight`, `pair_gross_weight`, `assortment_net_weight`, `high`, `width`, `length`.

### Vista del wizard

Formulario simple con lista readonly de líneas sin match y dos botones de acción.

---

## Importación de datos

Las líneas se importan usando el mecanismo estándar de Odoo (botón de importación en la
lista editable o2m). No se requiere código adicional para habilitarlo.

---

## Seguridad

| Acceso | Modelo | Grupo |
|---|---|---|
| CRUD | `purchase.container.line` | `purchase.group_purchase_user` |
| Read | `purchase.container.line` | `account.group_account_readonly` |
| RW | `purchase.container.line` | `account.group_account_invoice` |
| CRUD | `packing_list.warning.wizard` | `purchase.group_purchase_user` |
| CRUD | `packing.list.warning.line` | `purchase.group_purchase_user` |

---

## Decisiones de diseño

- **Matching por lote, no por producto:** evita errores de escritura al importar.
- **`move_id` en la línea:** permite filtrar visualmente las líneas sin match y es el
  vínculo entre packing list y el albarán de Odoo.
- **Una sola transacción:** si el usuario cancela el wizard, no queda ningún estado
  intermedio guardado en los albaranes.
- **No se modifica `purchase_container`:** toda la funcionalidad se añade mediante
  herencia, manteniendo la compatibilidad con futuras actualizaciones del módulo OCA.
- **Campos informativos sin validación:** `assortment`, `shippingmark`, `pairs`,
  `purchase_order` y `name` se importan tal cual, sin cruzar con otros modelos.
