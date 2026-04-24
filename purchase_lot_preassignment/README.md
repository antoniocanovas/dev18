# Purchase Lot Preassignment v18.0.0.2

## Descripción

Módulo para **Odoo 18** que pre-asigna lotes y números de serie a pedidos de venta en el momento de su confirmación,
vinculándolos con los pedidos de compra generados. Permite imprimir etiquetas de lotes desde compras y reservar
automáticamente los lotes recibidos para la entrega al cliente.

## Características

### Generación automática de lotes al confirmar venta

Al confirmar un pedido de venta, se crean automáticamente los `stock.lot` para todas las líneas con trazabilidad
por lote o número de serie, usando un **contador global incremental** por pedido:

- **Trazabilidad serial**: un lote por unidad, con nombre `{ref_cliente}-{SO}-001`, `002`, `003`...
  El contador es global entre todas las líneas del pedido, evitando colisiones entre líneas del mismo producto.
- **Trazabilidad por lote**: un lote por línea, con nombre `{ref_cliente}-{SO}`.
- El campo `ref` del lote siempre almacena el nombre del pedido de venta (`S00042`),
  permitiendo localizar todos los lotes de un pedido.

### Actualización de lotes al modificar cantidad vendida

Cuando se modifica la cantidad de una línea en un pedido de venta **ya confirmado** y el pedido de compra vinculado
está en **borrador**:

- **Decremento**: se eliminan los lotes sobrantes sin movimientos de stock activos y se regeneran todos
  con la nueva cantidad, manteniendo la numeración global coherente.
- **Incremento**: se crean los lotes adicionales con la numeración siguiente en la secuencia global.

Si el pedido de compra ya está **confirmado**:

- **Incremento**: se bloquea con un `UserError` indicando que hay que añadir una nueva línea en el presupuesto.
- **Decremento**: no se hace nada (el sobrante queda en stock).

### Reserva automática al recibir compra

Al validar una línea de recepción de compra (`stock.move.line` en estado `done`), el sistema localiza el pedido
de venta por la referencia del lote (`lot.ref`) y crea automáticamente la reserva del lote en el albarán de
salida correspondiente. Soporta tanto trazabilidad serial como por lote.

### Botón "Ver lotes" en ventas y albaranes

Desde el pedido de venta y desde el albarán se puede acceder a un wizard que muestra todos los lotes asociados
al pedido, buscando por `lot.ref = nombre del pedido de venta`.

### Botón "Etiquetas" en compras

Desde el pedido de compra se pueden imprimir etiquetas para los lotes vinculados a los pedidos de venta
relacionados. Formatos disponibles:

| Formato | Dimensiones |
|---------|------------|
| 4x12 | 43mm × 19mm |
| 2x7 | 99mm × 38mm |
| 4x7 | 43mm × 38mm |
| ZPL | Impresora Zebra |

## Estructura del módulo

```
purchase_lot_preassignment/
├── __manifest__.py
├── models/
│   ├── purchase_order.py       # Botón "Etiquetas" → wizard
│   ├── sale_order.py           # create_lots_for_sale_order, _delete_unused_lots, botón "Ver lotes"
│   ├── stock_move_line.py      # _reserve_lot_for_sale_order (auto-reserva al recibir)
│   └── stock_picking.py        # Botón "Ver lotes" en albaranes
├── data/
│   └── automated_actions.xml   # Acción 1: crear lotes al confirmar venta
│                               # Acción 2: reservar lote al recibir compra
├── report/
│   ├── purchase_lot_label_reports.xml
│   ├── purchase_lot_label_templates.xml
│   └── purchase_lot_label_zpl.xml
├── wizard/
│   ├── purchase_lot_view_wizard.py   # Selección y impresión de etiquetas
│   └── sale_lot_view_wizard.py       # Visualización de lotes en ventas/albaranes
└── security/
    └── ir.model.access.csv
```

## Dependencias

```python
depends = ["purchase", "stock", "purchase_stock", "web", "product", "sale", "sale_purchase"]
```

## Instalación

```bash
./odoo-bin -u purchase_lot_preassignment -d <base_de_datos>
```

## Flujo de trabajo

```
1. Confirmar pedido de venta
       ↓
2. Acción automática crea lotes (lot.ref = SO name, numeración global)
       ↓
3. Se crea pedido de compra vinculado (módulo shoes_dealer)
       ↓
4. [Opcional] Imprimir etiquetas desde compra → botón "Etiquetas"
       ↓
5. Recibir mercancía en albarán de compra
       ↓
6. Acción automática reserva lotes en albarán de venta
       ↓
7. Entregar al cliente con los lotes pre-asignados
```

## Licencia

LGPL-3 — Punt Sistemes
