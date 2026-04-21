# Shoes Intrastat Duty Estimation v18.0

## Descripción

Módulo complementario de `shoes_dealer` que añade la estimación de costes arancelarios
(intrastat duty) al producto de calzado. Permite calcular el **coste de aterrizaje estimado
por par** incluyendo el arancel aduanero, y lo usa como base del precio de venta recomendado
en lugar del exwork puro.

## Dependencias

```python
depends = ["product", "shoes_dealer", "intrastat_duty"]
```

## Campos añadidos a `product.template`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `intrastat_duty_id` | Many2one → `intrastat.duty` | Partida arancelaria asignada al producto |
| `estimated_pair_landed_cost` | Monetary (compute) | Coste estimado del par en EUR incluyendo el arancel |

## Lógica de cálculo

### `estimated_pair_landed_cost`

Campo computado no almacenado. Calcula el coste de aterrizaje del par en EUR:

| Tipo de producto | Fórmula |
|-----------------|---------|
| Surtido (`is_assortment`) | `exwork_single_euro × (1 + duty% / 100)` |
| Par (`is_pair`) | `exwork_euro × (1 + duty% / 100)` |
| Producto normal | `0` |

Donde `duty%` es el porcentaje de arancel de la partida `intrastat_duty_id`.

### `recommended_sale_price` (override)

Sobreescribe el cálculo de `shoes_dealer` para surtidos y pares, usando el coste de
aterrizaje como base en lugar del exwork directo:

```
base = exwork_single_euro × (1 + duty%) → para surtidos
base = exwork_euro × (1 + duty%)        → para pares
recommended_sale_price = base + base × sale_margin / 100
```

Para **productos normales** (ni surtido ni par), el cálculo estándar de `shoes_dealer`
se mantiene sin modificación: `exwork + exwork × sale_margin / 100`.

## Sincronización del arancel

El onchange `_sync_intrastat_duty` propaga automáticamente el cambio de `intrastat_duty_id`
entre el surtido y su par vinculado (y viceversa), evitando bucles con el contexto
`skip_intrastat_sync`.

## Vista

Añade los campos `intrastat_duty_id` y `estimated_pair_landed_cost` en el formulario de
producto, justo después del campo `exwork_single_euro` (en la pestaña Shoes Dealer).

## Instalación

```bash
./odoo-bin -u shoes_intrastat_duty -d <base_de_datos>
```

## Licencia

GPL-3 — Punt Sistemes
