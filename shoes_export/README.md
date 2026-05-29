# Shoes Export

Exportación de pedidos de venta del sector calzado a fichero Excel (.xlsx) con dos hojas especializadas: una para datos EAN de pares y otra para el detalle de líneas de venta.

## Dependencias

- `shoes_dealer`
- `shoes_campaign`

## Uso

### Desde la vista lista

Selecciona uno o varios pedidos y ejecuta la acción **Export EAN and SALE LINES to Excel** desde el menú de acciones (engranaje).

### Desde el formulario del pedido

Abre el pedido y pulsa el botón **Export Excel** visible en la cabecera del formulario. La acción también está disponible en el menú de acciones del formulario.

### Restricción multi-pedido

Se pueden seleccionar varios pedidos siempre que pertenezcan al mismo **cliente comercial** (`commercial_partner_id`). Los pedidos pueden ir facturados a delegaciones distintas del mismo grupo. Si se seleccionan pedidos de clientes diferentes, la acción muestra un error con los nombres en conflicto e impide la descarga.

### Fichero generado

El nombre del fichero sigue el patrón `<empresa>_<YYYYMMDD>_<pedido>.xlsx`. Se crea como adjunto del primer pedido seleccionado y se descarga automáticamente.

---

## Hoja 1 — EAN

Listado de **productos par** agregado por pedido y producto. Cada fila representa un par único dentro del pedido con la cantidad total acumulada de todos los surtidos y líneas donde aparece.

Los pares proceden de:
- Surtidos vendidos → explosión de su lista de materiales (BoM).
- Pares vendidos sueltos → directamente desde la línea.

| Columna | Origen |
|---|---|
| Núm pedido | `sale.order.name` |
| Marca | `order.shoes_campaign_id.product_brand_id.name` |
| Temporada | `order.shoes_campaign_id.name` |
| NombreWeb | `product.trade_name` (fallback al surtido padre) |
| Modelo | `product.product.name` |
| Color | `product.color_value_id.name` |
| Talla | `product.size_value_id.name` |
| quantity | Suma de unidades del par en todos los surtidos de la selección |
| Tip | `product.categ_id.name` |
| Código de barras | `product.barcode` |
| Desc corta | `product.shoes_last_id.description` |
| Material Exterior | `task.shoes_material_external1/2_id.name` + porcentaje |
| Plantilla | `task.shoes_material_lin_internal1/2_id.name` + porcentaje |
| Forro | `product.shoes_last_id.insole_material_id.name` |
| Punta | `product.shoes_last_id.toe` |
| Tacón | `product.shoes_last_id.heel_id.name` |
| Altura Tacón | `product.shoes_last_id.heel_height` |
| Coste | `sale.order.line.pair_price` |
| Moneda | `order.currency_id.name` |
| Origen | `product.intrastat_duty_id.country_id.code` |
| Partida Arancelaria | `product.intrastat_duty_id.intrastat_id.code` |

Los campos de materiales (`shoes_task_id.*`) se resuelven desde la tarea del par; si el par no tiene tarea asignada se usa la del surtido padre (`product_tmpl_set_id`).

---

## Hoja 2 — Surtidos

Una fila por **línea de venta**, incluyendo únicamente líneas de surtidos y pares. Cada surtido representa un bulto; la columna *Tallas* detalla la composición del surtido.

| Columna | Origen |
|---|---|
| Imagen | `product.image_1920` — incrustada a resolución completa, mostrada a 60 × 60 px. Descargable con clic derecho en Excel/LibreOffice. |
| NAVIMA PO NR. | `sale.order.name` |
| temporada | `order.shoes_campaign_id.name` |
| brand | `order.shoes_campaign_id.product_brand_id.name` |
| modelo | `product.product.name` |
| surtido | `product.assortment_attribute_id.name` |
| STYLE CODE | Nombre del producto + código de surtido |
| COLOR | `product.color_value_id.name` |
| categoría | `product.categ_id.name` |
| price | `sale.order.line.pair_price` (precio por par con descuentos aplicados) |
| moneda | `order.currency_id.name` |
| Tallas | Composición del surtido desde la BoM: `37x2, 38x3, …` |
| par_nota | `sale.order.line.pairs_count` — total de pares de la línea |
| bultos | `sale.order.line.product_uom_qty` — número de surtidos |
| pares_bul | Pares por surtido (`product.pairs_count`) |
| portes | `order.incoterm.name` |
| su_referencia | Referencia del cliente en la línea (módulo `sale_order_line_client_order_ref`) |

---

## Requisitos técnicos

- **openpyxl** debe estar instalado en el entorno Python del servidor. Si no está disponible, la acción muestra un aviso y no genera el fichero.
- La imagen incrustada usa `image_1920`; si el producto no tiene imagen la celda queda vacía sin interrumpir la exportación.
