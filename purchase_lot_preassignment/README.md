# Purchase Lot Preassignment v18.0.0.2

## Descripción

Módulo para **Odoo 18** que pre-asigna lotes y números de serie a pedidos de venta y de compra,
vinculándolos con los movimientos de stock correspondientes. Permite imprimir etiquetas de lotes
desde compras y reservar automáticamente los lotes recibidos para la entrega al cliente.

Módulo genérico: no depende de conceptos de dominio (surtidos, marcas, etc.). La lógica específica
de dominio (filtrado por `is_assortment`, prefijos en el nombre del lote, etc.) se implementa en
módulos que heredan de este, como `shoes_dealer`.

## Características

### Generación automática de lotes al confirmar venta

Al confirmar un pedido de venta, se crean automáticamente los `stock.lot` para todas las líneas con trazabilidad
por lote o número de serie, usando un **contador global incremental** por pedido:

- **Trazabilidad serial**: un lote por unidad, con nombre `{SO}-001`, `002`, `003`...
  El contador es global entre todas las líneas del pedido, evitando colisiones entre líneas del mismo producto.
- **Trazabilidad por lote**: un lote por línea, con nombre `{SO}`.
- El campo `ref` del lote almacena el nombre del pedido de venta (`S00042`).
- Si la compañía tiene `purchase_all_sale = False`, la cantidad de lotes creados es igual
  a la cantidad comprada (`purchase_line_id.product_qty`) en lugar de la cantidad vendida.

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

### Generación de lotes para pedidos de compra directos

Para pedidos de compra con productos de trazabilidad lot/serial **sin pedido de venta vinculado**
(compras de stock sin SO de origen), `create_lots_for_purchase_order` crea automáticamente los lotes:

- Nombre: `{PO}-001`, `{PO}-002`... con contador global entre todas las líneas del PO.
- El campo `ref` del lote almacena el nombre del pedido de compra.
- Se regeneran ante cualquier cambio de cantidad o añadir/eliminar líneas.

Los disparadores de sincronización (create/write/unlink en `purchase.order.line`) se implementan
en los módulos dependientes que conocen qué productos requieren pre-asignación de lotes.

### Reserva automática al recibir compra

Al validar una línea de recepción de compra (`stock.move.line` en estado `done`), el sistema:

1. Localiza el pedido de venta por `lot.ref` y busca el albarán de salida pendiente.
2. Para **trazabilidad serial**: reserva el lote en el albarán de salida solo si la entrega
   aún no está completa.
3. Para **trazabilidad por lote**: reserva la cantidad estrictamente necesaria para completar
   el pedido de venta, sin excederse.

### Botón "Ver lotes" en ventas y albaranes

Desde el pedido de venta y desde el albarán se puede acceder a un wizard que muestra los lotes asociados.

**En pedidos de venta:** busca lotes por `lot.ref = nombre del pedido de venta`.

**En albaranes de recepción:** la lógica depende del estado de procesamiento del packing list:

- **Post-procesamiento** (el albarán ya tiene move lines con lotes asignados):
  muestra únicamente los lotes en `picking.move_line_ids.lot_id`.
- **Pre-procesamiento** (sin move lines con lotes todavía): muestra todos los lotes del PO
  vinculado, excluyendo los que ya están asignados en move lines de otros albaranes del mismo PO.

**En albaranes de entrega:** busca lotes por `lot.ref = nombre del pedido de venta` del albarán.

### Botón "Etiquetas" en compras

Desde el pedido de compra se pueden imprimir etiquetas para los lotes de todos los pedidos de venta vinculados
y para los lotes creados directamente para ese PO. Formatos disponibles:

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
│   ├── purchase_order_line.py  # Declaración vacía (triggers implementados en módulos dependientes)
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
1. Crear pedido de compra con líneas de productos con trazabilidad (sin SO vinculado)
       ↓
2. Se crean automáticamente los lotes (lot.ref = PO name, numeración global)
       ↓
3. [Opcional] Imprimir etiquetas → botón "Etiquetas"
       ↓
4. Recibir mercancía → lotes quedan en stock disponibles para futuras ventas
```

## Licencia

LGPL-3 — Punt Sistemes
