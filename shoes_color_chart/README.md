# Shoes Color Chart v18.0.1.0.0

## Descripción

Gestión de fichas de color por campaña para productos de calzado. Permite definir qué colores
y surtidos están disponibles para cada modelo en cada campaña, y asignarlos masivamente a los
productos desde un wizard.

## Funcionalidad principal

### Fichas de color (`shoes.color.chart`)

Cada ficha agrupa los colores e ítems disponibles para un modelo dentro de una campaña.
Se accede desde la vista de campaña (proyecto) o desde el propio producto.

### Wizard de asignación masiva

Desde un producto `is_pair`, el botón **"Todos los surtidos"** asigna automáticamente
a la línea de atributo de surtido todos los valores de atributo vinculados a surtidos
del género del producto. La búsqueda excluye los surtidos marcados como `custom=True`
(creados automáticamente desde el wizard de cuadrícula de ventas), que son específicos
de un cliente y no deben aparecer en asignaciones genéricas.

### Wizard de copia de fichas

Permite duplicar una ficha de color de una campaña a otra, manteniendo la estructura
de colores e ítems.

## Modelos propios

| Modelo | Descripción |
|--------|-------------|
| `shoes.color.chart` | Ficha de color: asocia un modelo (task) con una campaña y sus colores disponibles |
| `shoes.color.chart.item` | Ítem de color dentro de una ficha (color + surtido + estado) |

## Campos añadidos a modelos estándar

| Modelo | Campo | Descripción |
|--------|-------|-------------|
| `product.template` | `shoes_color_chart_ids` | Fichas de color asociadas al producto |
| `project.project` | `shoes_color_chart_ids` | Fichas de color de la campaña |
| `project.task` | `shoes_color_chart_ids` | Fichas de color del modelo |
| `product.attribute` | (vistas) | Filtros y agrupaciones por atributo de color/surtido |

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
