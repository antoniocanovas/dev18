# Shoes Product SKU v18.0

## Descripción

Módulo para **Odoo 18** que amplía la gestión de productos de calzado con dos funcionalidades
complementarias:

1. **Referencia interna automática** (`default_code`): genera el código interno de cada variante
   (par o surtido) a partir de una composición configurable de hasta 5 componentes.

2. **Modelo `shoes.sku`**: referencia numérica secuencial única por combinación de **boceto de
   campaña + color**. Permite gestionar imágenes y datos del modelo antes de que el producto
   llegue a ser par o surtido, y relaciona todos los productos del mismo color bajo un código común.

La integración con el comercio electrónico (website_sale) se realiza a través del módulo
complementario **`shoes_ecommerce`**.

---

## Parte 1 — Referencia interna automática (`default_code`)

### Composición del SKU

El `default_code` se construye concatenando hasta 5 componentes en el orden definido por
`shoes_sku_item_ids` en la configuración de empresa:

| Componente | Campo de variante | Opciones |
|-----------|-------------------|---------|
| Campaña | `shoes_campaign_id` | `name` o `task_code_prefix` |
| Material | `material_id` | `name` o `code` |
| Fabricante | `manufacturer_id` | `name` o `ref` |
| Producto | `shoes_task_id.shoes_default_code_prefix` | `name` o prefijo de tarea |
| Color | `color_value_id` | `name` o `code` |

Cada componente puede llevar un prefijo de hasta 2 caracteres y puede desactivarse (`none`).
Si la tarea tiene `shoes_default_code_sufix`, se añade al final del código.

Solo se generan referencias para productos con `is_pair=True` o `is_assortment=True`.

### Cuándo se actualiza el `default_code`

| Evento | Condición | Acción |
|--------|-----------|--------|
| Ejecución de *"Create shoe pairs"* | `shoes_sku_update=True` | Actualiza el código de todas las variantes del surtido y del par |
| Creación de nuevas variantes | `shoes_sku_update=True` | Actualiza el código de la variante recién creada y sus hermanas |
| Acción manual *"⇒ Actualizar Códigos de variante"* | Siempre | Recalcula el código de todas las variantes del template seleccionado y revisa asignaciones de SKU |

---

## Parte 2 — Modelo `shoes.sku`

### Concepto

Un registro `shoes.sku` representa una referencia única por `(boceto, color)`. Es independiente
del número de variantes de talla o surtido que tenga ese modelo en ese color.

Esto permite:
- Subir fotografías del modelo antes de que el producto sea par o surtido.
- Tener un código estable y secuencial que agrupe todas las variantes del mismo modelo y color.
- Sincronizar la imagen principal entre todos los productos del mismo SKU.

### Campos

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | Char | Código numérico generado por secuencia. Único, no editable manualmente, no copiable. |
| `shoes_task_id` | Many2one → `project.task` | Boceto / modelo de campaña |
| `shoes_campaign_id` | Many2one → `project.project` | Campaña (related a `shoes_task_id.project_id`, almacenado) |
| `color_value_id` | Many2one → `product.attribute.value` | Color |
| `product_ids` | One2many → `product.product` | Variantes asociadas |
| `product_tmpl_set_id` | Many2one → `product.template` | Template del surtido (computed) |
| `product_tmpl_single_id` | Many2one → `product.template` | Template del par (computed) |
| `image` | Image | Imagen principal del modelo |
| `product_image_ids` | One2many → `product.image` | Galería de imágenes adicionales |

### Campos añadidos a modelos existentes

| Modelo | Campo | Tipo | Descripción |
|--------|-------|------|-------------|
| `product.product` | `shoes_sku_id` | Many2one → `shoes.sku` | SKU asignado a la variante. `copy=False`: al duplicar una variante o tarea no se hereda el SKU. |
| `product.product` | `shoes_sku_image_ids` | Many2many computed | Imágenes adicionales del SKU de **esta variante** (`shoes_sku_id.product_image_ids`). No mezcla colores ni modelos. |
| `product.template` | `shoes_sku_id` | Many2one computed | Primer SKU de las variantes del template (solo lectura, para visualización). |
| `product.template` | `shoes_sku_count` | Integer computed | Número de SKUs distintos asignados a las variantes. |
| `project.task` | `shoes_sku_ids` | One2many → `shoes.sku` | SKUs vinculados a esta tarea (boceto). |
| `project.task` | `shoes_sku_count` | Integer computed | Número de SKUs de la tarea. |
| `project.project` | `shoes_sku_ids` | One2many → `shoes.sku` | SKUs de la campaña. |
| `project.project` | `shoes_sku_count` | Integer computed | Número de SKUs de la campaña. |

### Ciclo de vida del SKU

```
shoes_create_product()                 create_shoe_pairs()
        │                                      │
        ▼                                      ▼
 Un SKU por color                  Variantes is_pair /
 (shoes_color_chart_item_ids)       is_assortment creadas
 Solo si no existe ya uno                      │
 con ese color para la tarea                   ▼
                              _assign_shoes_sku() en cada variante:
                              1. Busca SKU por (tarea, color)
                              2. Si no existe, crea SKU nuevo
```

**Al crear el producto desde el boceto** (`shoes_create_product`): se crea un `shoes.sku` por
cada color incluido en `shoes_color_chart_item_ids` de la tarea, con `color_value_id` asignado.
Si ya existe un SKU para esa combinación `(tarea, color)` no se duplica. Requiere que la tarea
tenga al menos un color definido (validado previamente por `shoes_color_chart`).

**Al crear variantes** de par o surtido: el sistema busca el SKU por `(tarea, color)`. Si no
existe, crea un SKU nuevo con todos los datos. El resultado se asigna al campo `shoes_sku_id` de
la variante.

**Al duplicar una tarea**: `shoes_sku_id` tiene `copy=False` en `product.product`, por lo que las
variantes de la tarea duplicada arrancan sin SKU asignado y `_assign_shoes_sku` les generará uno
nuevo basándose en la nueva tarea + color.

### Sincronización de imágenes

| Dirección | Trigger | Acción |
|-----------|---------|--------|
| SKU → variante | Cambio en `shoes.sku.image` | Escribe `image_variant_1920` en todos los `product.product` de `product_ids` usando el valor ya normalizado (`sku.image` post-write) |
| Variante → SKU | Cambio en `product.product.image_variant_1920` | Actualiza `shoes_sku_id.image` |

El flag de contexto `_sku_image_sync=True` evita bucles infinitos en ambas direcciones.

### Seguridad

| Grupo | Permisos |
|-------|---------|
| `base.group_user` (usuario interno) | Lectura |
| `product.group_product_manager` | Lectura, escritura, creación, borrado |

No se puede eliminar un SKU si tiene variantes de producto asociadas.

---

## Configuración de empresa

En **Ajustes → Compañía**, pestaña **Shoes SKU** (grupo *Sequence*):

| Campo | Descripción |
|-------|-------------|
| `shoes_sku_sequence_id` | Secuencia usada para generar el nombre de los registros `shoes.sku`. Por defecto: secuencia "Shoes SKU" (longitud 5, sin prefijo ni sufijo, sin huecos). |
| `shoes_sku_update` | Activa la actualización automática del `default_code` al crear variantes |
| `shoes_sku_item_ids` | Orden de los 5 componentes del `default_code` (deben estar todos presentes) |
| `shoes_code_<componente>` | Selección entre `code`, `name` o `none` para cada componente |
| `shoes_code_<componente>_prefix` | Prefijo de 2 caracteres para cada componente |

---

## Vistas y menús

### Menú *Marketing → SKU*

Acceso a la lista y formulario de `shoes.sku` desde el menú principal de Shoes Dealer.

**Vista lista**: imagen · nombre · boceto · color (resto opcionales).

**Vista formulario**: imagen principal, datos del SKU (boceto, campaña, color), productos
relacionados (surtido y par), pestaña de imágenes adicionales. Las variantes asociadas son
accesibles mediante el botón estadístico, no como pestaña.

### Botones de acceso rápido

| Modelo | Ubicación | Condición de visibilidad |
|--------|-----------|--------------------------|
| `project.task` | Botón estadístico en el form | `is_shoes_campaign = True` |
| `project.project` | Botón estadístico en el form | `is_shoes_campaign = True` |
| `product.template` | Botón estadístico en el form | Tiene `shoes_task_id` y al menos un SKU asignado |

### Campos añadidos a vistas existentes

| Vista | Campo añadido |
|-------|---------------|
| Lista de variantes (`product.product`) | `shoes_sku_id` después de `name` (visible por defecto) |
| Formulario de producto (`product.template`) | `shoes_sku_id` (computed, readonly) bajo `shoes_model_material` |

### Botones en vista lista de SKU

La vista lista de `shoes.sku` incluye dos botones de acción por fila:

| Botón | Icono | Acción |
|-------|-------|--------|
| Import Images | `fa-upload` | Abre el wizard de importación de imágenes para ese SKU |
| Samples | `fa-users` | Abre la lista de muestras (`shoes.sample`) asociadas al SKU |

---

## Wizard de muestras (`shoes.sample.task.wizard`)

El wizard se abre desde el botón **Samples** del formulario de tarea y presenta una matriz SKU × contacto para gestionar las muestras de una tarea de campaña.

### Columnas del wizard

Las columnas representan los contactos con el campo **Muestras** activado (`shoes_samples = True`). El encabezado de cada columna muestra:

- El campo **Ref** del contacto (`res.partner.ref`) si está definido.
- El **nombre** del contacto si no tiene ref.

Esto permite usar referencias cortas para contactos habituales y evitar columnas excesivamente anchas.

### Filas del wizard

Cada fila muestra el SKU con:

- Imagen del modelo (miniatura 36×36 px).
- Nombre del SKU.
- Color (si está definido en `color_value_id`), en texto secundario bajo el nombre.

### Celda

Cada celda contiene un campo de texto de 2 caracteres (mayúsculas automáticas) con el tipo de muestra. Si se deja vacío y existía una muestra previa, esta se elimina al guardar.

---

## Módulo complementario

| Módulo | Propósito |
|--------|-----------|
| `shoes_ecommerce` | Integración con `website_sale`: muestra las imágenes del SKU de cada variante en el carrusel del producto web y en el formulario de edición de variante |

---

## Dependencias

```python
depends = [
    "base", "product",
    "shoes_dealer", "shoes_campaign", "shoes_color_chart",
]
```

---

## Licencia

GPL-3 — Punt Sistemes SL
