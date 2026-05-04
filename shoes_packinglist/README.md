# Shoes Packing List v18.0.1.0.0

## Descripción

Módulo para **Odoo 18** que gestiona los packing lists de contenedores de importación de calzado. Permite importar las líneas del packing list de un contenedor, emparejarlas con los movimientos de stock pendientes, dividir los albaranes según el contenido del contenedor, asignar los números de serie a las move lines y actualizar automáticamente los datos de peso, volumen y dimensiones en productos y lotes.

Hereda del módulo `purchase_container` y añade toda la lógica de emparejamiento y actualización de datos de recepción.

---

## Modelos

### `purchase.container.line`

Línea del packing list de un contenedor. Cada línea representa una caja (surtido) con su lote asignado.

| Campo | Descripción |
|-------|-------------|
| `container_id` | Contenedor al que pertenece |
| `shoes_campaign` | Temporada |
| `name` | Nombre del producto |
| `color` | Color |
| `pairs` | Número de pares en la caja |
| `purchase_order` | Referencia del pedido de compra |
| `assortment` | Código de surtido |
| `lot` | Número de serie / lote |
| `volume` | Volumen (m³) |
| `pair_net_weight` | Peso neto por par (kg) |
| `pair_gross_weight` | Peso bruto por par (kg) |
| `assortment_net_weight` | Peso neto del surtido (kg) |
| `assortment_gross_weight` | Peso bruto del surtido (kg) |
| `shippingmark` | Shipping mark |
| `width` / `length` / `high` | Dimensiones de la caja (cm) |
| `move_id` | `stock.move` emparejado (asignado al procesar) |

Los campos de texto se limpian automáticamente de espacios y tabulaciones al crear o escribir.

### `product.product`

Añade el campo `width_length_high` (Char) para almacenar las dimensiones de la caja en formato `W×L×H (cm)`.

### `stock.lot`

Añade los campos `weight`, `net_weight`, `volume` y `width_length_high` para registrar los datos físicos del lote tal como aparecen en el packing list.

---

## Acción principal: Update from Packing List

El botón **"Update from Packing List"** en el contenedor ejecuta `action_update_from_packing_list`:

### Validaciones previas

1. El contenedor debe tener un agente de transporte (`shipping_agent_id`).
2. Debe haber líneas en el packing list.
3. Debe existir al menos un albarán de recepción pendiente para ese agente.

### Algoritmo de emparejamiento de lotes

Para cada línea del packing list se busca el `stock.move` correcto en los albaranes pendientes:

**Prioridad 1 — Move line pre-asignada:** si ya existe una `stock.move.line` con ese lote en un albarán pendiente (asignada por un contenedor anterior), se usa el move de esa línea directamente.

**Prioridad 2 — Búsqueda por capacidad:** entre los moves del producto:
- Primero se filtran por la cadena de pedido de venta (`lot.ref = SO name`).
- Si no hay resultado, se busca por producto sin restricción.
- Entre los candidatos, se elige el primero que tenga **capacidad** disponible: `(lot lines existentes + asignaciones de esta sesión) < product_qty`.

El conteo de sesión (`session_lot_counts`) permite manejar correctamente contenedores con múltiples líneas del mismo producto sin que colisionen entre sí.

Si alguna línea no puede emparejarse, se abre el **wizard de aviso** que lista las líneas sin match y permite continuar (saltando esas líneas) o cancelar.

### División de albaranes

Tras el emparejamiento, para cada albarán implicado:

1. Se calculan los moves **emparejados** (tienen líneas de contenedor apuntando a ellos) y los **no emparejados** (el resto del albarán).
2. **Moves parcialmente cubiertos** (el contenedor solo cubre parte de la qty del move): se llama a `move._split(backorder_qty)` para reducir el move original a la qty del contenedor y crear un nuevo move con el resto. Si hay `stock.move.line` pre-asignadas con lotes no incluidos en el contenedor, se redistribuyen al nuevo move.
3. Los moves no emparejados (y los nuevos moves del split) se mueven a un albarán backorder via `_split_picking`. El backorder se confirma automáticamente para que quede disponible en futuras actualizaciones.
4. El albarán original queda con solo los moves del contenedor y se le asigna `container_id`.

### Asignación de lotes a move lines

`_assign_lots_to_moves` crea las `stock.move.line` con el lote específico:

1. Elimina las move lines sin lote (genéricas de `action_assign`) de los moves emparejados.
2. Crea una move line por línea de packing list con `lot_id` y `quantity=1.0`.
3. Es idempotente: si el lote ya está en una move line, no lo crea de nuevo.

### Actualización de datos de producto y lote

`_update_product_weights_from_packing_list` actualiza, por cada línea procesada:

| Destino | Campos actualizados |
|---------|-------------------|
| `stock.lot` | `weight`, `net_weight`, `volume`, `width_length_high` |
| `product.template` (surtido) | `weight`, `net_weight`, `volume` |
| `product.product` (surtido) | `width_length_high` |
| `product.template` (par, via `product_tmpl_single_id`) | `weight` (pair_gross), `net_weight` (pair_net), `volume / pairs` |

La actualización de producto está deduplicada por `product.id` para evitar escrituras repetidas del mismo producto en el mismo contenedor.

---

## Wizards

### Wizard de aviso de líneas no emparejadas (`packing.list.warning.wizard`)

Se abre automáticamente si alguna línea del packing list no pudo emparejarse con ningún move. Muestra las líneas problemáticas (lote, producto, pedido de compra) y ofrece dos opciones:

- **Continuar**: procesa solo las líneas emparejadas, ignorando las demás.
- **Cancelar**: vuelve al contenedor para revisar los datos.

### Wizard de validación del contenedor (`container.validate.wizard`)

Permite validar todos los albaranes pendientes del contenedor en un único paso:

1. Solicita la **ubicación de destino** (ubicación interna o de tránsito).
2. Actualiza `location_dest_id` en el albarán, los moves y las move lines.
3. Valida todos los albaranes con `skip_backorder=True`.

---

## Flujo de trabajo completo

```
1. Crear contenedor en purchase_container con el agente de transporte
         ↓
2. Importar líneas del packing list (purchase.container.line)
         ↓
3. Pulsar "Update from Packing List"
         ↓
4. Sistema empareja cada lote con su stock.move
   [Si hay líneas sin match → wizard de aviso]
         ↓
5. Se divide el albarán:
   - Albarán original ← moves del contenedor
   - Albarán backorder ← moves no cubiertos por el contenedor
         ↓
6. Se crean move lines con lotes específicos en el albarán original
         ↓
7. Se actualizan pesos, volúmenes y dimensiones en producto y lote
         ↓
8. [Repetir pasos 2-7 para el siguiente contenedor del mismo envío]
         ↓
9. Pulsar "Validar" → wizard de validación → seleccionar ubicación → confirmar
```

---

## Dependencias

```python
depends = ["purchase_container", "stock", "account", "product_net_weight"]
```

## Instalación

```bash
./odoo-bin -u shoes_packinglist -d <base_de_datos>
```

---

## Licencia

LGPL-3 — Ingenieriacloud
