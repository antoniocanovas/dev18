# Shoes Packing List v18.0.1.0.0

## Descripción

Módulo para **Odoo 18** que gestiona los packing lists de contenedores de importación de calzado. Permite importar las líneas del packing list de un contenedor, emparejarlas con los movimientos de stock pendientes, dividir los albaranes según el contenido del contenedor, asignar los números de serie a las move lines, actualizar automáticamente los datos de peso, volumen y dimensiones en productos y lotes, y **generar facturas de compra** agrupando contenedores por agente y moneda.

Hereda del módulo `purchase_container` y añade toda la lógica de emparejamiento, actualización de datos de recepción y facturación.

---

## Modelos

### `purchase.container` (extensión)

Campos añadidos sobre el modelo base de `purchase_container`:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `container_line_ids` | One2many | Líneas del packing list del contenedor |
| `container_line_count` | Integer (computed) | Número de líneas del packing list |
| `currency_id` | Many2one → `res.currency` | Moneda de compra, calculada desde `shipping_agent_id.property_purchase_currency_id`. Editable posteriormente. |
| `duty_currency_id` | Many2one → `res.currency` | Moneda para el cálculo de aranceles |
| `currency_exchange` | Float (6 decimales) | Tipo de cambio: 1 unidad de `currency_id` = N unidades de `duty_currency_id` |
| `invoice_ids` | Many2many → `account.move` | Facturas generadas para este contenedor |
| `invoice_count` | Integer (computed) | Número de facturas asociadas |

**Campo calculado `name`** (override de `purchase_container`):

El nombre del contenedor es directamente el valor del campo `code`.

---

### `purchase.container.line`

Línea del packing list de un contenedor. Cada línea representa una caja (surtido) con su lote asignado.

| Campo | Descripción |
|-------|-------------|
| `container_id` | Contenedor al que pertenece |
| `shoes_campaign` | Temporada |
| `name` | Nombre del producto |
| `color` | Color |
| `pair_qty` | Número de pares en la caja |
| `quantity` | Cantidad de surtidos (defecto 1) |
| `purchase_order` | Referencia del pedido de compra |
| `client_order_ref` | Referencia del pedido del cliente final |
| `tariff_heading` | Partida arancelaria |
| `shippingmark` | Shipping mark |
| `assortment` | Código de surtido |
| `lot` | Número de serie / lote |
| `volume` | Volumen (m³) |
| `pair_net_weight` | Peso neto por par (kg) |
| `pair_gross_weight` | Peso bruto por par (kg) |
| `assortment_net_weight` | Peso neto del surtido (kg) |
| `assortment_gross_weight` | Peso bruto del surtido (kg) |
| `high` / `width` / `length` | Dimensiones de la caja (cm) |
| `move_id` | `stock.move` emparejado (asignado al procesar) |
| `currency_id` | Related a `container_id.currency_id` (moneda de compra para `price`) |
| `price` | Precio de compra (monetario en `currency_id`) |
| `duty_currency_id` | Related a `container_id.duty_currency_id` (moneda arancelaria para `price_duty`) |
| `price_duty` | Precio arancelario calculado: `price × currency_exchange`. Si `duty_currency_id` coincide con `currency_id` o no está definido, equivale a `price`. Almacenado. |
| `invoice_line_id` | Many2one → `account.move.line`. Línea de factura a la que está vinculada. Vacío = pendiente de facturar. |

Los campos de texto (`shoes_campaign`, `name`, `color`, `purchase_order`, `assortment`, `lot`, `shippingmark`) se limpian automáticamente de espacios y tabulaciones al crear o escribir.

---

### `product.product` (extensión)

Añade el campo `width_length_high` (Char) para almacenar las dimensiones de la caja en formato `W×L×H (cm)`.

---

### `stock.lot` (extensión)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `weight` | Float | Peso bruto del surtido (kg) |
| `net_weight` | Float | Peso neto del surtido (kg) |
| `volume` | Float | Volumen (m³) |
| `width_length_high` | Char | Dimensiones en formato `W×L×H (cm)` |
| `container_line_id` | Many2one → `purchase.container.line` | Línea del packing list de la que procede el lote (`ondelete="set null"`) |
| `container_id` | Many2one → `purchase.container` | Related a `container_line_id.container_id`, store=True |

---

### `account.move` (extensión)

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `container_ids` | Many2many → `purchase.container` | Contenedores facturados en esta factura. Visible como `many2many_tags` en facturas de compra (readonly). |

---

## Acciones disponibles en `purchase.container`

### Botón "Update" — Actualizar desde packing list

Ejecuta `action_update_from_packing_list`. Ver sección [Acción principal](#acción-principal-update-from-packing-list).

### Botón "Container reception" — Wizard de validación

Abre el wizard para validar todos los albaranes del contenedor en un único paso. Ver [Wizards](#wizards).

### Botón "Packing List" — Imprimir

Imprime el informe QWeb del packing list del contenedor. Llama primero a `action_update_from_packing_list` para asegurar que los datos estén actualizados; si hay líneas sin emparejar, abre el wizard de aviso en lugar de imprimir.

### Botón "Invoice" — Generar factura

Genera una factura de proveedor (`in_invoice`) a partir de las líneas del contenedor pendientes de facturar. Ver [Facturación](#facturación).

### Stat button "Invoices"

Visible solo cuando `invoice_count > 0`. Abre la lista de facturas asociadas al contenedor.

---

## Acción principal: Update from Packing List

El botón **"Update"** ejecuta `action_update_from_packing_list`:

### Validaciones previas

1. El contenedor debe tener un agente de transporte (`shipping_agent_id`).
2. Debe haber líneas en el packing list.
3. Debe existir al menos un albarán de recepción pendiente para ese agente.

### Algoritmo de emparejamiento de lotes

Para cada línea del packing list se busca el `stock.move` correcto en los albaranes pendientes:

**Prioridad 1 — Move line pre-asignada:** si ya existe una `stock.move.line` con ese lote en un albarán pendiente (asignada por un módulo anterior), se usa el move de esa línea directamente.

**Prioridad 2 — Búsqueda por capacidad:** entre los moves del producto:
- Primero se filtran por la cadena de pedido de venta (`lot.ref = SO name`).
- Si no hay resultado, se busca por producto sin restricción.
- Entre los candidatos, se elige el primero que tenga **capacidad disponible**: `(lot lines existentes + asignaciones de esta sesión) < product_qty`.

El conteo de sesión (`session_lot_counts`) permite manejar correctamente contenedores con múltiples líneas del mismo producto sin colisiones.

Si alguna línea no puede emparejarse, se abre el **wizard de aviso** con las líneas problemáticas.

### División de albaranes

Tras el emparejamiento, para cada albarán implicado:

1. Se calculan los moves **emparejados** y los **no emparejados**.
2. **Moves parcialmente cubiertos**: se llama a `move._split(backorder_qty)` para reducir el move original a la qty del contenedor y crear un nuevo move con el resto. Las move lines pre-asignadas con lotes no incluidos en el contenedor se redistribuyen al nuevo move.
3. Los moves no emparejados se mueven a un albarán backorder via `_split_picking`. El backorder se confirma automáticamente.
4. El albarán original queda con solo los moves del contenedor y se le asigna `container_id`.

### Asignación de lotes a move lines

`_assign_lots_to_moves`:

1. Elimina las move lines sin lote (genéricas de `action_assign`) de los moves emparejados.
2. Crea una move line por línea de packing list con `lot_id` y `quantity=1.0`.
3. Es idempotente: si el lote ya está en una move line no lo crea de nuevo.

### Actualización de datos de producto y lote

`_update_product_weights_from_packing_list` actualiza por cada línea procesada:

| Destino | Campos actualizados |
|---------|-------------------|
| `stock.lot` | `weight`, `net_weight`, `volume`, `product_length`, `product_height`, `product_width`, `dimensional_uom_id`, `container_line_id` |
| `product.product` (surtido) | `weight`, `net_weight`, `product_length`, `product_height`, `product_width`, `dimensional_uom_id` |
| `product.template` (par, via `product_tmpl_single_id`) | `weight` (pair_gross), `net_weight` (pair_net), `volume / pairs` |

La actualización de producto está deduplicada por `product.id` para evitar escrituras repetidas del mismo producto en el mismo contenedor. Las dimensiones se registran siempre en cm (`uom.product_uom_cm`).

---

## Facturación

### Generación desde un contenedor (botón "Invoice")

```python
container.action_create_invoice()
```

### Generación desde varios contenedores (acción contextual en lista)

Seleccionar uno o más contenedores en la vista lista → menú **⚙ Acción** → **Invoice**.

### Condiciones previas

- Todos los contenedores seleccionados deben tener el **mismo `shipping_agent_id`**.
- Todos deben tener la **misma `currency_id`**.
- Debe haber al menos una línea pendiente (sin `invoice_line_id`) con `move_id` y producto detectado.

### Algoritmo de generación

1. Se recogen todas las líneas `purchase.container.line` sin `invoice_line_id` y con producto detectado vía `move_id`.
2. Se agrupan por `(product_id, shippingmark)`.
3. Para cada grupo se crea una línea de factura:
   - `quantity` = número de líneas del grupo
   - `price_unit` = `sum(price) / quantity` (media ponderada; garantiza que el subtotal coincide con `sum(price)`)
   - `account_id` = cuenta de gasto del producto (`get_product_accounts()['expense']`)
   - `tax_ids` = impuestos de compra del producto filtrados por compañía
   - `name` = nombre del producto + ` - shippingmark` (si existe)
4. Se crea la factura de proveedor (`in_invoice`) con:
   - `partner_id` = `shipping_agent_id`
   - `currency_id` = `currency_id` del contenedor
   - `container_ids` = contenedores que tenían líneas pendientes
5. Cada `purchase.container.line` queda enlazada a su `account.move.line` via `invoice_line_id`.

### Facturación parcial

Las líneas ya enlazadas (`invoice_line_id` definido) se omiten en ejecuciones posteriores. Esto permite generar **una segunda factura** para las líneas que quedaron pendientes de un contenedor ya facturado parcialmente, simplemente volviendo a ejecutar la acción sobre ese contenedor.

### Visibilidad en la factura

El campo `container_ids` aparece en la factura de compra encima de las líneas de factura, en modo `many2many_tags` (solo lectura). Permite identificar de qué contenedores procede cada factura.

---

## Wizards

### Wizard de aviso de líneas no emparejadas (`packing.list.warning.wizard`)

Se abre automáticamente si alguna línea del packing list no pudo emparejarse con ningún move. Muestra las líneas problemáticas (lote, producto, pedido de compra) y ofrece dos opciones:

- **Continuar**: procesa solo las líneas emparejadas, ignorando las demás.
- **Cancelar**: vuelve al contenedor para revisar los datos.

### Wizard de validación del contenedor (`container.validate.wizard`)

Permite validar todos los albaranes pendientes del contenedor en un único paso:

1. Solicita la **ubicación de destino**.
2. Actualiza `location_dest_id` en el albarán, los moves y las move lines.
3. Valida todos los albaranes con `skip_backorder=True`.

---

## Flujo de trabajo completo

```
1. Crear contenedor en purchase_container
   (agente de transporte, duty_currency_id, currency_exchange si aplica)
         ↓
2. Importar líneas del packing list (purchase.container.line)
         ↓
3. Pulsar "Update"
         ↓
4. Sistema empareja cada lote con su stock.move
   [Si hay líneas sin match → wizard de aviso → continuar o cancelar]
         ↓
5. División del albarán:
   - Albarán original ← moves del contenedor (container_id asignado)
   - Albarán backorder ← moves no cubiertos
         ↓
6. Move lines con lotes específicos creadas en el albarán original
         ↓
7. Pesos, volúmenes y dimensiones actualizados en producto y lote
         ↓
8. [Repetir pasos 2-7 para el siguiente contenedor del mismo envío]
         ↓
9. Pulsar "Container reception" → seleccionar ubicación → confirmar validación
         ↓
10. Pulsar "Invoice" (o seleccionar varios contenedores → ⚙ Invoice)
    → Se genera la factura de proveedor agrupando líneas por (producto, shippingmark)
    → Las líneas quedan vinculadas a la factura (invoice_line_id)
```

---

## Dependencias

```python
depends = [
    "purchase_container",
    "stock",
    "account",
    "product_net_weight",
    "product_dimension",
]
```

## Instalación

```bash
./odoo-bin -u shoes_packinglist -d <base_de_datos>
```

---

## Licencia

LGPL-3 — Ingenieriacloud
