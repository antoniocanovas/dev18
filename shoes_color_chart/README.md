# Shoes Color Chart v18.0.1.0.0

## Descripción

Gestión de cartas de color por campaña para productos de
calzado. Permite definir qué combinaciones de color, material
y fabricante están disponibles en cada campaña y asignarlas
masivamente desde wizards. Incluye filtrado dinámico en vistas
de tarea y horma para restringir los valores al contexto de
la campaña activa.

## Funcionalidad principal

### Carta de color (`shoes.color.chart.item`)

Modelo propio que representa una combinación de campaña,
material, fabricante y color. Actúa como catálogo de
combinaciones válidas para una campaña. Incluye validación
de unicidad y nombre calculado automáticamente.

### Wizard de asignación masiva (`shoes.color.chart.wizard`)

Desde la vista de campaña, permite añadir múltiples colores
de golpe a la carta filtrando por fabricante y material.
Valida que el fabricante tenga referencia y el material
tenga código antes de crear los ítems.

### Wizard de copia de carta (`shoes.color.chart.copy.wizard`)

Duplica todos los ítems de la carta de color de una campaña
origen a otra campaña destino.

### Actualización de colores en producto (`product.template`)

Acción **"Actualizar colores desde carta de campaña"**:
sincroniza la línea de atributo de color del producto con
los colores de la carta de la campaña, filtrados por material.

Acción **"Todos los surtidos"**: asigna a la línea de
atributo de surtido todos los valores del género del producto,
excluyendo surtidos `custom=True` (específicos de cliente).

### Filtrado de colores en línea de atributo

Modelo `product.template.attribute.line`. Campo computado
`campaign_value_ids`: cuando la línea corresponde al atributo
de color y el producto tiene campaña, devuelve solo los
colores de la carta (fabricante + material + campaña).
En cualquier otro caso devuelve todos los valores del atributo.

### Material auxiliar por compañía (`res.company`)

Campo `project_auxiliar_material_id`: proyecto (campaña
simulada) que representa los materiales generales no
vinculados a ninguna campaña real, a efectos de propuestas
de marketing.

### Materiales (`product.material`)

Campos añadidos: fabricante (`manufacturer_id`), código de
fabricante (`manufacturer_code`), código combinado
(`material_manufacturer_code`) y campañas asociadas
(`shoes_campaign_ids`).

El dominio de `shoes_campaign_ids` permite seleccionar tanto
proyectos marcados como `is_shoes_campaign=True` como el
proyecto de material auxiliar configurado en la compañía.

### Filtrado en tareas y hormas

`project.task` y `shoes.last` exponen
`project_auxiliar_material_id` como campo computado
(valor de la compañía) para usarlo como variable en los
dominios de las vistas y restringir los materiales disponibles.

## Modelos propios

| Modelo | Descripción |
|--------|-------------|
| `shoes.color.chart.item` | Combo campaña/fabricante/material/color |
| `shoes.color.chart.wizard` | Asignación masiva de colores a carta |
| `shoes.color.chart.copy.wizard` | Copia de carta entre campañas |

## Campos añadidos a modelos estándar

**`product.template`**
- Acciones para sincronizar colores desde carta de campaña
  y surtidos por género del producto.

**`product.template.attribute.line`**
- `campaign_value_ids`: colores filtrados por carta cuando
  la línea es el atributo de color y el producto tiene campaña.

**`product.attribute.value`**
- `code`: código corto del valor de atributo.

**`project.project`**
- `shoes_color_chart_item_ids`: ítems de carta de la campaña.
- `color_value_ids`, `manufacturer_value_ids`,
  `material_value_ids`: conjuntos únicos de colores,
  fabricantes y materiales usados en la carta.

**`project.task`**
- `shoes_color_chart_item_ids`: colores asignados al modelo.
- `project_auxiliar_material_id`: proyecto auxiliar de la
  compañía (para dominios de vista).

**`shoes.last`**
- `project_auxiliar_material_id`: proyecto auxiliar de la
  compañía (para dominios de vista).

**`product.material`**
- `shoes_campaign_ids`: campañas en las que se usa el material.
- `manufacturer_id`, `manufacturer_code`,
  `material_manufacturer_code`: fabricante y códigos.
- `company_project_auxiliar_material_id`: proyecto auxiliar
  de la compañía (dominio de `shoes_campaign_ids`).

**`res.company`**
- `project_auxiliar_material_id`: proyecto de material
  auxiliar por compañía.

## Dependencias

```python
depends = [
    "product", "project",
    "partner_product_attribute_value",
    "shoes_dealer", "shoes_campaign",
]
```

## Licencia

GPL-3 — Punt Sistemes SL
