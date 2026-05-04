# Shoes Purchase v18.0.1.0.0

## Descripción

Módulo para **Odoo 18** que añade dos operaciones sobre pedidos de compra en borrador: **dividir** un pedido en dos y **fusionar** varios pedidos en uno. Ambas operaciones mantienen la integridad de los lotes pre-asignados por `purchase_lot_preassignment`.

---

## Funcionalidades

### 1. Dividir pedido de compra

Accesible desde el botón **"Dividir pedido"** (icono tijeras) en el formulario del pedido, visible solo en estado borrador.

El wizard muestra un campo many2many con las **líneas a conservar en el pedido original**. Las líneas no seleccionadas se moverán al nuevo pedido.

**Selección de líneas:**

El campo permite añadir líneas en múltiples pasos. El botón "Añadir una línea" abre un diálogo con todas las líneas del pedido, con una barra de búsqueda que permite:

- **Filtrar por texto**: artículo, pedido de venta o shipping mark.
- **Agrupar por**: pedido de venta, shipping mark o artículo.

Se pueden hacer varias rondas de selección (añadir, revisar, añadir más) antes de confirmar la división.

**Resultado tras pulsar "Dividir pedido":**

1. Se crea un nuevo pedido de compra con los mismos datos de cabecera (proveedor, campaña, divisa, fecha prevista, referencia proveedor, notas).
2. Las líneas no seleccionadas se trasladan al nuevo pedido.
3. Se regeneran los lotes del pedido original (`create_lots_for_purchase_order`).
4. Se regeneran los lotes del nuevo pedido (`create_lots_for_purchase_order`).
5. Se muestra una notificación con el nombre del nuevo pedido creado.

**Validaciones:**
- El pedido debe estar en estado borrador.
- Debe seleccionarse al menos una línea para el pedido original.
- Debe quedar al menos una línea para el nuevo pedido.

---

### 2. Fusionar pedidos de compra

Accesible desde la vista lista de pedidos de compra mediante la **acción contextual "Fusionar pedidos"** (seleccionar varios pedidos → Acción).

Se abre un wizard de confirmación que muestra:

| Campo | Descripción |
|-------|-------------|
| Pedidos a fusionar | Lista de los pedidos seleccionados |
| Pedido superviviente | El pedido con el ID más alto (el más reciente) |
| Notas fusionadas | Concatenación de las notas de todos los pedidos |
| Error de validación | Mensaje si no se cumplen las condiciones |

**Condiciones para fusionar:**
- Mínimo 2 pedidos seleccionados.
- Todos en estado **borrador**.
- Todos del **mismo proveedor**.
- Todos de la **misma campaña** (`shoes_campaign_id`).

**Resultado tras pulsar "Fusionar":**

1. Todas las líneas de los pedidos absorbidos se trasladan al pedido superviviente.
2. `date_planned` del superviviente se actualiza al valor más reciente entre todos los pedidos.
3. Las notas se fusionan (concatenadas con salto de línea).
4. Se eliminan los lotes sin uso de los pedidos absorbidos (`_delete_unused_po_lots`).
5. Los pedidos absorbidos se eliminan (`unlink`).
6. Se regeneran los lotes del superviviente (`create_lots_for_purchase_order`).
7. Se abre el formulario del pedido superviviente.

---

## Integridad de lotes

Ambas operaciones llaman a los métodos de `purchase_lot_preassignment` para mantener coherencia:

| Método | Cuándo se llama |
|--------|----------------|
| `create_lots_for_purchase_order()` | Tras dividir (en ambos POs) y tras fusionar (en el superviviente) |
| `_delete_unused_po_lots()` | En cada PO absorbido antes de eliminarlo |

---

## Estructura del módulo

```
shoes_purchase/
├── __manifest__.py
├── models/
│   └── purchase_order.py          # action_open_split_wizard, action_open_merge_wizard
├── wizard/
│   ├── purchase_split_wizard.py   # TransientModel: purchase_order_id, line_ids, action_split
│   ├── purchase_split_wizard_views.xml
│   ├── purchase_merge_wizard.py   # TransientModel: purchase_order_ids, survivor_id, action_merge
│   └── purchase_merge_wizard_views.xml
├── views/
│   └── purchase_order_views.xml   # Botón "Dividir pedido" en formulario
├── data/
│   └── purchase_merge_server_action.xml  # Acción contextual en vista lista
└── security/
    └── ir.model.access.csv
```

---

## Vistas de `purchase.order.line` añadidas

El módulo añade vistas standalone para `purchase.order.line` usadas en el diálogo "Añadir una línea" del wizard de división, y extiende la vista de búsqueda base de Odoo para que los filtros aparezcan tanto en el diálogo como en el menú del módulo OCA `purchase_order_line_menu`:

| Vista | Tipo | Descripción |
|-------|------|-------------|
| `purchase_order_line_list_split` | list (priority=10) | Columnas: artículo, pedido de venta, shipping mark, cantidad, precio |
| `purchase_order_line_search_split` | search (hereda `purchase.purchase_order_line_search`) | Añade búsqueda por pedido de venta y shipping mark; group-by por pedido de venta y shipping mark |

---

## Dependencias

```python
depends = [
    "purchase",
    "sale_purchase",
    "shoes_dealer",
    "purchase_lot_preassignment",
    "shoes_shippingmark",
]
```

## Instalación

```bash
./odoo-bin -u shoes_purchase -d <base_de_datos>
```

---

## Licencia

LGPL-3 — Punt Sistemes
