# Spec: shoes_purchase — Wizard de división de pedido de compra

**Fecha:** 2026-05-04
**Módulo:** `shoes_purchase` (nuevo)
**Contexto:** Odoo 18 Enterprise

---

## 1. Objetivo

Permitir dividir un pedido de compra en estado **borrador** en dos pedidos: el original conserva las líneas que el usuario selecciona en el wizard, y un nuevo pedido recibe el resto.

---

## 2. Módulos de contexto

| Módulo | Aportación relevante |
|---|---|
| `shoes_dealer` | `purchase.order.shoes_campaign_id`, `purchase.order.line.pairs_count`, `purchase.order.line.assortment_pair_id`, flujo de creación de POL desde SOL |
| `purchase_lot_preassignment` | `create_lots_for_purchase_order()`, `_delete_unused_po_lots()`, lógica de `stock.lot.ref` |
| `shoes_shippingmark` | `purchase.order.line.pnt_sale_type_id`, validación de cantidad en POL con `sale_line_id` |
| `sale_purchase` (Odoo base) | `purchase.order.line.sale_line_id`, `purchase.order.line.sale_order_id`, `purchase.order._get_sale_orders()` |

---

## 3. Estructura del módulo

```
shoes_purchase/
├── __manifest__.py
├── __init__.py
├── wizard/
│   ├── __init__.py
│   └── purchase_split_wizard.py
├── views/
│   ├── purchase_split_wizard_views.xml
│   └── purchase_order_views.xml
└── security/
    └── ir.model.access.csv
```

---

## 4. Modelo: `purchase.split.wizard` (TransientModel)

### 4.1 Campos

| Campo | Tipo | Atributos | Descripción |
|---|---|---|---|
| `purchase_order_id` | Many2one → `purchase.order` | required, readonly | PO origen |
| `available_line_ids` | Many2many → `purchase.order.line` | compute, no-store | Todas las líneas del PO; define el dominio de `line_ids` |
| `line_ids` | Many2many → `purchase.order.line` | domain=`[('id','in',available_line_ids)]` | Líneas que el usuario elige **conservar** en el PO original |

### 4.2 Método `action_split()`

**Precondiciones (UserError si no se cumplen):**
1. `purchase_order_id.state == 'draft'` — defensa en profundidad.
2. `line_ids` no vacío — "Selecciona al menos una línea para conservar en el pedido original."
3. `line_ids != purchase_order_id.order_line` — "Debes dejar al menos una línea en el nuevo pedido."

**Algoritmo:**

```
lines_to_move = purchase_order_id.order_line - line_ids

nuevo_po = purchase.order.create({
    partner_id, shoes_campaign_id, currency_id,
    company_id, date_planned, partner_ref, notes
})                                         # copiados del PO original

lines_to_move.write({'order_id': nuevo_po.id})   # reasignación directa

purchase_order_id.create_lots_for_purchase_order()  # limpia y recrea lotes directos del original
nuevo_po.create_lots_for_purchase_order()           # crea lotes directos del nuevo PO

return display_notification(nuevo_po.name)
```

**Nota sobre lotes de SO:** los lotes con `ref = SO.name` no requieren acción explícita. Al reasignar las POL al nuevo PO, `nuevo_po._get_sale_orders()` (= `order_line.sale_order_id`) encontrará automáticamente los SOs vinculados y sus lotes.

### 4.3 Método auxiliar en `purchase.order`

```python
def action_open_split_wizard(self):
    return {
        'name': 'Dividir pedido de compra',
        'type': 'ir.actions.act_window',
        'res_model': 'purchase.split.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {'default_purchase_order_id': self.id},
    }
```

---

## 5. Vistas

### 5.1 Formulario del wizard (`purchase_split_wizard_views.xml`)

- **Cabecera:** nombre del PO origen (readonly).
- **Cuerpo:** tree many2many editable de `line_ids` con selección múltiple. Columnas visibles: producto, plantilla de producto, temporada (`shoes_campaign_id`), cliente SO (`sale_order_id.partner_id`), shipping mark (`pnt_sale_type_id`), cantidad, precio unitario, pares (`pairs_count`).
- **Barra de búsqueda de la tree:** filtros/agrupaciones por `shoes_campaign_id`, `sale_order_id.partner_id`, `product_id`, `product_tmpl_id`, `pnt_sale_type_id`.
- **Pie:** botón **"Dividir pedido"** (`action_split`, tipo `object`) y botón **"Cancelar"** (`special="cancel"`).

### 5.2 Extensión de `purchase.order` (`purchase_order_views.xml`)

Añade mediante `xpath` un botón en la barra de botones del formulario de `purchase.order`:

```xml
<button name="action_open_split_wizard"
        string="Dividir pedido"
        type="object"
        invisible="state != 'draft'"
        class="btn-secondary"/>
```

---

## 6. Seguridad

`ir.model.access.csv` concede acceso completo (`CRUD`) al wizard `purchase.split.wizard` para el grupo `purchase.group_purchase_user`.

---

## 7. Lógica de lotes — resumen

| Origen del lote | `stock.lot.ref` | Acción en la división |
|---|---|---|
| Creado desde SO (`create_lots_for_sale_order`) | `SO.name` | Ninguna: sigue vinculado al SO, accesible desde el nuevo PO vía `_get_sale_orders()` |
| Creado desde PO directo (`create_lots_for_purchase_order`) | `PO.name` | Se eliminan los huérfanos (`_delete_unused_po_lots`) y se recrean en ambos POs |

---

## 8. Validaciones y casos borde

| Caso | Comportamiento |
|---|---|
| `line_ids` vacío al confirmar | `UserError`: "Selecciona al menos una línea para conservar en el pedido original." |
| Todas las líneas seleccionadas | `UserError`: "Debes dejar al menos una línea en el nuevo pedido." |
| PO no en borrador (defensa) | `UserError`: "Solo se pueden dividir pedidos en estado borrador." |
| Líneas con `sale_line_id` en `lines_to_move` | El enlace `SOL.purchase_line_id` apunta al POL; tras el `write`, el POL está en el nuevo PO — trazabilidad intacta |
| Líneas con cantidad 0 | Se tratan igual que el resto |
| PO sin lotes directos | `create_lots_for_purchase_order()` no crea nada — comportamiento seguro |

---

## 9. Dependencias del `__manifest__.py`

```python
'depends': [
    'purchase',
    'sale_purchase',
    'shoes_dealer',
    'purchase_lot_preassignment',
    'shoes_shippingmark',
],
```
