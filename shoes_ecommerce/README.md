# Shoes eCommerce v18.0

## Descripción

Módulo complementario para **Odoo 18** que integra el modelo `shoes.sku` con el comercio
electrónico (`website_sale`).

Requiere tener instalado **`shoes_product_sku`**. No se instala automáticamente: debe activarse
explícitamente cuando la instalación utilice `website_sale`.

---

## Funcionalidad

### 1 — Imágenes SKU en el carrusel del producto web

Al navegar por la tienda online, el carrusel de imágenes de cada variante de producto muestra,
además de las imágenes propias de la variante y del template, las imágenes adicionales
(`product_image_ids`) del SKU de **esa variante concreta**.

La integración se realiza sobreescribiendo `product.product._get_images()`, que `website_sale`
usa para construir la lista de imágenes del carrusel:

```
Carrusel = imagen principal de variante
         + imágenes extra de variante  (product_variant_image_ids)
         + imágenes extra de template  (product_template_image_ids)
         + imágenes del SKU            (shoes_sku_id.product_image_ids)  ← añadidas por este módulo
```

Cada variante muestra exclusivamente las imágenes del SKU que le corresponde (su color/modelo).
No hay replicación de datos: las imágenes del SKU se leen dinámicamente en cada petición.

### 2 — Sección *SKU Media* en el formulario de edición de variante (backend)

En el formulario de edición rápida de variante (`product.product_variant_easy_edit_view`),
accesible desde la pestaña de variantes del producto, aparece una sección **SKU Media**
(solo lectura) justo debajo de *Extra Variant Media*. Muestra las imágenes del SKU asignado
a esa variante concreta.

La sección se oculta automáticamente si la variante no tiene SKU con imágenes. El campo
`shoes_sku_image_ids` que la alimenta está definido en `shoes_product_sku` como Many2many
computed sobre `shoes_sku_id.product_image_ids`.

---

## Dependencias

```python
depends = [
    "shoes_product_sku",
    "website_sale",
]
```

---

## Licencia

GPL-3 — Punt Sistemes SL
