# Shoes Campaign v18.0

## Descripción

Módulo para **Odoo 18** que amplía la gestión de campañas de calzado (`project.project` con
`is_shoes_campaign = True`) y sus bocetos (`project.task`). Añade datos de modelo, vistas
específicas y lógica de codificación interna de producto.

---

## Dependencias

```python
depends = ["shoes_dealer"]
```

---

## Campos en `project.task`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `is_shoes_campaign` | Boolean related | `True` si la tarea pertenece a una campaña de calzado |
| `shoes_default_code_prefix` | Char | Prefijo de referencia interna del boceto |
| `shoes_default_code_sufix` | Char computed+store | Sufijo de referencia interna. Se calcula como `shoes_sufix_model_code_prefix` (empresa) + `project_id.name`. Editable manualmente. Se recalcula al cambiar el proyecto. |
| `product_brand_id` | Many2one related | Marca del proyecto (related a `project_id.product_brand_id`) |
| `manufacturer_id` | Many2one | Fabricante del modelo |
| `code` | Char | Código de tarea (generado por secuencia al crear) |
| `gender` | Selection | Género (Man / Woman / Children) |
| `shoes_material_id` | Many2one | Material principal |
| `shoes_last_id` | Many2one | Horma |
| `shoes_manufacturer_ref` | Char | Referencia del fabricante |
| `exwork` | Float | Precio exwork |
| `shoes_model_material` | Char computed+store | Concatenación de prefijo, código de material y ref de fabricante |
| `trade_name` | Char | Nombre comercial para exportación |
| `shoes_product_tmpl_id` | Many2one | Producto creado desde este boceto |
| `sale_campaign_ids` | Many2many computed+store | Campañas de venta en las que participa el boceto (campaña propia + campañas de venta del producto) |
| `project_ribbon_label` | Char computed | Nombre del proyecto del boceto cuando es distinto del proyecto activo en el que se visualiza. Vacío si coincide. Usado para mostrar el ribbon en la vista kanban. |

### Campo `project_ribbon_label`

Permite identificar visualmente en el kanban de una campaña los bocetos que pertenecen a otra
campaña pero aparecen por estar vinculados a ella a través de `sale_campaign_ids`.

- Devuelve `project_id.name` cuando `task.project_id.id != context.active_id`.
- Devuelve `False` cuando el boceto pertenece a la campaña que se está visualizando o no hay
  contexto de campaña activa.

---

## Campos en `project.project`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `is_shoes_campaign` | Boolean | Marca el proyecto como campaña de calzado |
| `product_brand_id` | Many2one | Marca asociada a la campaña |
| `task_code_prefix` | Char | Prefijo para la secuencia de código de bocetos |
| `task_code_sequence` | Integer | Contador interno de la secuencia de bocetos |

---

## Campos en `res.company`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `shoes_sufix_model_code_prefix` | Char (max 2) | Prefijo que se antepone al nombre del proyecto al calcular `shoes_default_code_sufix` |

---

## Vistas modificadas

### Vista kanban de `project.task`

- **Ribbon de campaña**: en el kanban de tareas de un proyecto, los bocetos que pertenecen a
  otro proyecto (visibles por `sale_campaign_ids`) muestran un ribbon en la esquina superior
  derecha con el nombre de su proyecto original. Se implementa con la clase CSS estándar de Odoo
  `ribbon ribbon-top-right` y el campo `project_ribbon_label`.

- **Imagen del modelo**: sustituye `displayed_image_id` por una imagen de altura fija (150 px)
  con `object-fit: cover`, que ocupa el ancho completo de la tarjeta.

### Vista lista de `project.task`

Añade columnas opcionales: marca, producto, código, fabricante, material, género, categoría,
horma, exwork, arancel, peso, URL, modelo+material, prefijo y sufijo de referencia.

### Vista formulario de `project.task`

- Botón **Create product** (visible solo en campañas de calzado).
- Pestaña **Shoe model**: datos del modelo (marca, fabricante, material, exwork, imagen...).
- Pestaña **Shoe details**: materiales de composición, cierre, altura, tipo de caña.
- Campos `shoes_default_code_prefix` y `shoes_default_code_sufix` visibles junto a la fecha límite.

### Vistas de `project.project`

- Formulario principal: añade `is_shoes_campaign`, `product_brand_id`, `task_code_prefix` y
  botón para actualizar márgenes de venta de todos los productos de la campaña.
- Formulario simplificado (creación rápida): mismos campos en grupo adicional.

---

## Acciones de tarea modificadas

El dominio de las acciones estándar de Odoo para ver las tareas de un proyecto
(`act_project_project_2_project_task_all` y `dblc_proj`) se amplía a:

```python
[('sale_campaign_ids', 'in', [active_id])]
```

Esto incluye tanto los bocetos nativos del proyecto como los bocetos de otras campañas cuyos
productos se venden en esta campaña (vía `sale_campaign_ids`).

---

## Licencia

LGPL-3
