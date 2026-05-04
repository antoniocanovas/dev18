# Shoes Dealer v18.0.1.0.0

## Descripción

Módulo para **Odoo 18** especializado en la gestión de empresas de calzado. Cubre el ciclo completo:
catálogo de productos (surtidos y pares), campañas comerciales, generación de compras vinculadas a ventas,
trazabilidad de pares, márgenes por par y conversión de precios exwork a EUR.

El concepto central es el **surtido** (caja de zapatos con múltiples tallas) y el **par** (producto individual
de una talla específica). El módulo automatiza la relación entre ambos y vincula las ventas de surtidos con
las compras al fabricante.

## Conceptos clave

| Concepto | Descripción |
|----------|-------------|
| **Surtido** | Producto que contiene múltiples tallas (ej: 36x2, 37x3, 38x2). Tiene BOM. |
| **Par** | Producto individual de una talla y color. Se genera automáticamente desde el surtido. |
| **Campaña** | Proyecto que agrupa los modelos de una temporada. Define el tipo de cambio y el margen. |
| **Exwork** | Precio de fábrica en moneda del fabricante. Se convierte a EUR usando el tipo de cambio de campaña. |
| **Assortment pair** | Registro de trazabilidad de cada par dentro de un movimiento de surtido. |

## Configuración inicial (res.company)

Antes de usar el módulo hay que configurar en **Ajustes → Compañía**:

| Campo | Descripción |
|-------|-------------|
| `assortment_attribute_id` | Atributo de producto que identifica el surtido |
| `size_attribute_id` | Atributo de talla |
| `color_attribute_id` | Atributo de color |
| `assortment_prefix` | Prefijo de referencia para surtidos (ej: `S.`) |
| `single_prefix` | Prefijo para pares (ej: `P.`) |
| `exwork_currency_id` | Moneda por defecto de los precios exwork |
| `shoes_assortment_tracking` | Trazabilidad de surtidos (`lot`, `serial`, ninguno) |
| `shoes_pair_tracking` | Trazabilidad de pares |
| `shoes_pair_uom_id` | Unidad de medida para pares |
| `shoes_categ_sync` | Sincroniza categoría contable automáticamente |
| `purchase_all_sale` | **Ver sección "Compra neta" más abajo** |

## Flujo de trabajo

### 1. Crear el catálogo

**Surtidos predefinidos** (`Zapatos → Surtidos`):
Define las distribuciones de tallas estándar (ej: `PACK1` = 36x2, 37x3, 38x2).
Cada surtido tiene un género y un código. No se puede modificar si ya está asignado a un atributo de producto.

**Hormas y tacones** (`Zapatos → Hormas / Tacones`):
Catálogo de hormas con material de suela, plantilla, plataforma, tipo de punta y altura de tacón.

**Materiales** (`Zapatos → Materiales`):
Catálogo de materiales con imagen y código.

---

### 2. Crear un producto surtido

1. Crear `product.template` con atributos de **color** y **surtido**.
2. Rellenar en la pestaña **Shoes Dealer**:
   - **Campaña**, fabricante, material, horma, peso por par
   - **Exwork** (precio de fábrica del surtido) y **Exwork single** (precio del par)
   - **Shipping** (gastos de envío)
   - **Margen** (`sale_margin` en %) y **precio recomendado** (calculado en tiempo real)

El precio recomendado se calcula como `exwork + exwork × margen / 100`. Si el módulo
`shoes_intrastat_duty` está instalado, la base del cálculo pasa a ser el coste de
aterrizaje estimado (exwork + arancel aduanero) en lugar del exwork directo. Ver README
de ese módulo para más detalle.
3. Ejecutar la acción **"Create shoe pairs"**. El sistema:
   - Crea el `product.template` del par con atributos de color y talla
   - Crea variantes del surtido (una por color × surtido)
   - Asigna el prefijo de referencia (`S.` / `P.`)
   - Genera el código de campaña incremental
   - Crea los BOM de cada variante del surtido (líneas = pares por talla)
   - Sincroniza género, fabricante, material y peso al par
   - Actualiza `standard_price` en variantes y crea registros de proveedor

---

### 3. Vender un surtido

En el pedido de venta, cada línea de surtido permite:

- **Surtido estándar**: el BOM define la distribución de tallas.
- **Surtido personalizado**: se introduce manualmente en formato `36x2,37x5,38x3`.
  El sistema valida que las tallas existan y que los pares estén creados.

Campos calculados en la línea:

| Campo | Descripción |
|-------|-------------|
| `pairs_count` | Total de pares (surtido × cantidad de cajas) |
| `pair_price` | Precio por par (`precio_total ÷ pairs_count`) |
| `special_pair_price` | Precio especial por par (recalcula el precio unitario) |
| `custom_assortment_pairs` | Pares totales del surtido personalizado |

**Al confirmar el pedido**, se crea automáticamente una línea en un pedido de compra al fabricante
(buscando primero un PO en borrador del mismo proveedor). La línea de compra queda vinculada a la
línea de venta mediante `purchase_line_id`.

---

### 4. Modificar cantidad en venta confirmada

| Situación | Resultado |
|-----------|-----------|
| PO en borrador, qty baja | Actualiza qty en compra, borra lotes sobrantes y regenera |
| PO en borrador, qty sube | Actualiza qty en compra, crea los lotes adicionales |
| PO confirmada, qty sube | **Error**: indica añadir nueva línea en el presupuesto |
| PO confirmada, qty baja | No modifica la compra ni los lotes (el sobrante queda en stock) |
| Sin PO (qty neta = 0), qty cambia | Sincroniza lotes si corresponde |

Añadir una nueva línea a una venta ya confirmada también genera automáticamente
la línea de compra correspondiente (si el producto es surtido).

---

### 5. Compra neta (`purchase_all_sale`)

El campo `purchase_all_sale` en `res.company` (pestaña **Shoes Dealer**, grupo "Sale and purchases")
controla cuántas unidades se compran al confirmar una venta:

**`True` (por defecto):** se compra la totalidad de lo vendido, sin considerar el stock disponible.

**`False`:** se calcula la cantidad neta a comprar:

```
qty_to_buy = qty_vendida − stock_disponible − entradas_libres_pendientes
```

Donde:
- **stock disponible**: unidades en ubicaciones internas no reservadas para otros pedidos,
  más las ya reservadas para el albarán de salida de este pedido. Si el cliente tiene
  *shipping marks* exclusivos (`shoes_shippingmark`), solo se cuenta el stock compatible.
  Si el tipo de reserva del albarán es "no reservar", se usa el stock físicamente libre.
- **entradas libres pendientes**: movimientos de compra pendientes de recibir sin pedido
  de venta vinculado (`purchase_line_id.sale_line_id = False`).

Reglas especiales:
- Los **surtidos personalizados** (`product_custom_attribute_value_ids`) siempre compran
  la cantidad completa, independientemente del campo.
- Si `qty_to_buy ≤ 0`, no se crea línea de compra ni lotes para esa línea.
- Los lotes creados por `purchase_lot_preassignment` reflejan la cantidad comprada,
  no la vendida.

---

### 6. Recibir la compra

Al validar el albarán de recepción, el automatismo de `purchase_lot_preassignment` reserva los lotes
en el albarán de venta.

Cuando una `stock.move.line` llega a estado `done`, si el producto es un surtido, el sistema crea
registros `assortment.pair` para cada par contenido (parseando las tallas y cantidades del BOM).
Estos registros permiten consultar el inventario de pares por separado del de surtidos.

---

### 7. Facturar

Las líneas de factura heredan automáticamente:

| Campo | Cálculo |
|-------|---------|
| `pairs_count` | `qty × pares del producto` |
| `cost_price` | `pairs_count × exwork_single_euro` |
| `shoes_margin` | `ingresos - cost_price` |
| `shoes_pair_margin` | `shoes_margin ÷ pairs_count` |
| `pair_price_sale` | `ingresos ÷ pairs_count` |

---

## Automatismos

| Trigger | Acción |
|---------|--------|
| Write en `product.template` (exwork, fabricante, campaña) | Actualiza `standard_price` en variantes y proveedores |
| Unlink en `product.template.attribute.value` (color/talla de surtido) | Limpia colores/tallas no usados del par |
| Write en `stock.move.line` → `state = done` (surtido) | Crea registros `assortment.pair` |
| Cron diario | Elimina `assortment.pair` con cantidad 0 |
| Write en `sale.order` → `state = sale` | Crea lotes (via `purchase_lot_preassignment`) |

---

## Modelos propios

| Modelo | Descripción |
|--------|-------------|
| `shoes.assortment` | Plantillas de distribución de tallas |
| `shoes.assortment.line` | Línea de talla + cantidad dentro de un surtido |
| `shoes.last` | Catálogo de hormas |
| `shoes.heel` | Catálogo de tipos de tacón |
| `shoes.pair.weight` | Pesos estándar por par (bruto y neto) |
| `product.material` | Catálogo de materiales |
| `assortment.pair` | Registro de trazabilidad de pares en movimientos |

---

## Dependencias

```python
depends = [
    # Odoo
    "crm", "sale_management", "sale_product_matrix", "account",
    "purchase", "stock", "mrp", "sale_mrp", "project",
    "base_automation", "sale_commission", "uom",
    "l10n_es_edi_facturae",
    # OCA
    "product_brand", "product_net_weight",
    "sale_product_template_tags", "product_variant_sale_price",
    "sale_product_image",
    # Custom
    "purchase_lot_preassignment",
]
```

**Módulos opcionales que amplían funcionalidad:**

| Módulo | Funcionalidad añadida |
|--------|-----------------------|
| `shoes_shippingmark` | Exclusividad de stock por Shipping Mark en el cálculo de compra neta |
| `shoes_intrastat_duty` | Precio recomendado calculado sobre coste de aterrizaje (exwork + arancel) |

---

## Instalación

```bash
./odoo-bin -u shoes_dealer,purchase_lot_preassignment -d <base_de_datos>
```

---

## Licencia

AGPL-3 — Serincloud SL / Punt Sistemes
