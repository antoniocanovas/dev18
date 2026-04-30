# Purchase Lot Preassignment v18.0.0.2

## Descripción

Módulo para **Odoo 18** que pre-asigna lotes y números de serie a pedidos de venta y de compra,
vinculándolos con los movimientos de stock correspondientes. Permite imprimir etiquetas de lotes
desde compras y reservar automáticamente los lotes recibidos para la entrega al cliente.

## Características

### Generación automática de lotes al confirmar venta

Al confirmar un pedido de venta, se crean automáticamente los `stock.lot` para todas las líneas con trazabilidad
por lote o número de serie, usando un **contador global incremental** por pedido:

- **Trazabilidad serial**: un lote por unidad, con nombre `{ref_cliente}-{SO}-001`, `002`, `003`...
  El contador es global entre todas las líneas del pedido, evitando colisiones entre líneas del mismo producto.
- **Trazabilidad por lote**: un lote por línea, con nombre `{ref_cliente}-{SO}`.
- El campo `ref` del lote almacena el nombre del pedido de venta (`S00042`),
  permitiendo localizar todos los lotes de un pedido.
- Si la compañía tiene `purchase_all_sale = False`, la cantidad de lotes creados es igual
  a la cantidad comprada (`purchase_line_id.product_qty`) en lugar de la cantidad vendida,
  para reflejar únicamente los surtidos que realmente se van a recepcionar.

### Limpieza y regeneración de lotes de venta

Los lotes se sincronizan automáticamente en los siguientes eventos:

| Evento | Acción |
|--------|--------|
| Modificar cantidad (PO en borrador) | Elimina sobrantes y regenera |
| Modificar cantidad (sin PO) | Elimina sobrantes y regenera |
| Eliminar línea de venta | Elimina los lotes sin movimientos de esa línea |
| Cancelar pedido de venta | Elimina todos los lotes sin movimientos activos |
| Pasar a presupuesto | Elimina todos los lotes sin movimientos activos |
| Re-confirmar pedido | Limpia lotes previos y recrea con la cantidad actualizada |

Los lotes no se eliminan si tienen movimientos de stock activos (ya recepcionados).

### Generación automática de lotes para pedidos de compra directos

Para pedidos de compra de productos `is_assortment` **sin pedido de venta vinculado**
(compras de stock sin SO de origen), se crean automáticamente los lotes usando el nombre
del pedido de compra como base:

- Nombre: `{PO}-001`, `{PO}-002`... con contador global entre todas las líneas del PO.
- El campo `ref` del lote almacena el nombre del pedido de compra.
- Se regeneran ante cualquier cambio de cantidad o añadir/eliminar líneas.
- Visibles en el wizard de etiquetas junto a los lotes de SO vinculados.

### Reserva automática al recibir compra

Al validar una línea de recepción de compra (`stock.move.line` en estado `done`), el sistema:

1. Localiza el pedido de venta por `lot.ref` y busca el albarán de salida pendiente.
2. Para **trazabilidad serial**: reserva el lote en el albarán de salida solo si la entrega
   aún no está completa (cantidad reservada < cantidad pedida). Si la entrega ya está
   cubierta (p.ej. con stock previo), el lote recibido se queda en stock sin asignarse.
3. Para **trazabilidad por lote**: reserva la cantidad estrictamente necesaria para completar
   el pedido de venta, sin excederse.

### Botón "Ver lotes" en ventas y albaranes

Desde el pedido de venta y desde el albarán se puede acceder a un wizard que muestra todos los lotes asociados
al pedido, buscando por `lot.ref = nombre del pedido de venta`.

### Botón "Etiquetas" en compras

Desde el pedido de compra se pueden imprimir etiquetas para los lotes de todos los pedidos de venta vinculados
**y** para los lotes creados directamente para ese PO (compras sin SO). Formatos disponibles:

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
│   ├── purchase_order.py       # _delete_unused_po_lots, create_lots_for_purchase_order, botón "Etiquetas"
│   ├── purchase_order_line.py  # Triggers create/write/unlink → sincronización de lotes de PO
│   ├── sale_order.py           # create_lots_for_sale_order, _delete_unused_lots, action_cancel/draft
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
│   ├── purchase_lot_view_wizard.py   # Selección y impresión de etiquetas (SO + PO directo)
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

## Flujo de trabajo — Venta vinculada a compra

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
   (solo si la entrega no está ya completa por stock previo)
       ↓
7. Entregar al cliente con los lotes pre-asignados
```

## Flujo de trabajo — Compra directa de stock

```
1. Crear pedido de compra con líneas de surtido (sin SO vinculado)
       ↓
2. Se crean automáticamente los lotes (lot.ref = PO name, numeración global)
       ↓
3. [Opcional] Imprimir etiquetas → botón "Etiquetas"
       ↓
4. Recibir mercancía → lotes quedan en stock disponibles para futuras ventas
```

## Licencia

LGPL-3 — Punt Sistemes
