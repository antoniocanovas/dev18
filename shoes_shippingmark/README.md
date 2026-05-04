# Shoes Shipping Mark v18.0.1.0.0

## Descripción

Módulo para **Odoo 18** que introduce el concepto de **Shipping Mark** en el ciclo de venta, compra y logística de calzado. Una Shipping Mark identifica el destino comercial (cliente, canal o marca) de un lote de mercancía, permitiendo controlar qué stock puede reservarse para qué cliente cuando existen restricciones de exclusividad.

El modelo subyacente es `sale.order.type` (módulo OCA `sale_order_type`), reutilizado como etiqueta logística de destino.

---

## Funcionalidades

### 1. Shipping Mark por defecto en compañía

`res.company` añade el campo `default_shippingmark_id`. Al crear un partner empresa, se le asigna automáticamente esta Shipping Mark como valor por defecto, eliminando la necesidad de configurarlo manualmente en cada cliente.

### 2. Shipping Marks exclusivos por cliente

`res.partner` añade el campo `shoes_shippingmark_ids` (Many2many). Si el cliente tiene al menos una Shipping Mark configurada, el sistema solo le reservará stock cuyos lotes tengan una Shipping Mark compatible. Si el campo está vacío, puede recibir stock de cualquier Shipping Mark.

| Campo en partner | Significado |
|------------------|-------------|
| `sale_type` | Shipping Mark por defecto (renombrado de "Default Sales Type") |
| `shoes_shippingmark_ids` | Lista de Shipping Marks exclusivas permitidas |

### 3. Asignación automática en líneas de compra

`purchase.order.line` añade `pnt_sale_type_id` (Shipping Mark). Se asigna automáticamente al crear la línea:

- Si la línea proviene de una venta: se copia el `type_id` del pedido de venta.
- Si es una compra directa sin SO: se asigna el `default_shippingmark_id` de la compañía.

Las líneas de compra vinculadas a una venta no pueden modificar su cantidad directamente; el cambio debe realizarse desde la línea de venta.

### 4. Trazabilidad de Shipping Mark en lotes

`stock.lot` añade `shippingmark_id`. Al crear lotes mediante `purchase_lot_preassignment`, la Shipping Mark del pedido de venta se propaga automáticamente a cada lote a través del contexto `shippingmark_id`. Esto permite saber, en todo momento, para qué cliente/marca fue creado cada lote.

### 5. Reserva de stock filtrada por Shipping Mark

Al ejecutar `_action_assign` en movimientos de salida de productos surtido (`is_assortment=True`):

1. Se comprueba si el cliente destinatario tiene `shoes_shippingmark_ids` configuradas.
2. Si las tiene, se pasa `shoes_allowed_shippingmark_ids` en el contexto.
3. `stock.quant._gather` filtra los quants para devolver solo aquellos cuyo `lot_id.shippingmark_id` esté en la lista permitida.

Esto garantiza que un cliente con exclusividad nunca reciba stock etiquetado para otro cliente.

---

## Modelos modificados

| Modelo | Campo añadido | Descripción |
|--------|--------------|-------------|
| `res.company` | `default_shippingmark_id` | Shipping Mark por defecto para nuevos partners empresa |
| `res.partner` | `shoes_shippingmark_ids` | Shipping Marks exclusivas del cliente |
| `sale.order` | `type_id` (renombrado) | Mostrado como "Shipping Mark" en la interfaz |
| `sale.order.type` | — | Restricción UNIQUE en nombre |
| `stock.lot` | `shippingmark_id` | Shipping Mark del lote (propagada desde la venta) |
| `purchase.order.line` | `pnt_sale_type_id` | Shipping Mark de la línea de compra |
| `stock.move` | `_action_assign` | Filtrado de reservas por exclusividad |
| `stock.quant` | `_gather` | Filtrado de quants por `shippingmark_id` del lote |

---

## Flujo de trabajo

```
1. Configurar default_shippingmark_id en la compañía
          ↓
2. [Opcional] Configurar shoes_shippingmark_ids en clientes con exclusividad
          ↓
3. Confirmar pedido de venta con type_id (Shipping Mark)
          ↓
4. Se crean lotes con shippingmark_id = type_id del pedido (vía purchase_lot_preassignment)
          ↓
5. Se crea línea de compra con pnt_sale_type_id = type_id
          ↓
6. Al reservar el albarán de salida:
   - Sin exclusividad → cualquier quant disponible
   - Con exclusividad → solo quants cuyo lot.shippingmark_id está permitido
```

---

## Dependencias

```python
depends = ["sale_order_type", "stock", "purchase"]
```

## Instalación

```bash
./odoo-bin -u shoes_shippingmark -d <base_de_datos>
```

---

## Licencia

GPL-3 — Punt Sistemes
