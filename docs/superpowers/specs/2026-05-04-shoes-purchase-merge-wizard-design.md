# Spec: shoes_purchase — Wizard de fusión de pedidos de compra

**Fecha:** 2026-05-04
**Módulo:** `shoes_purchase` (extensión)
**Contexto:** Odoo 18 Enterprise — complementa el wizard de división ya implementado

---

## 1. Objetivo

Permitir fusionar N pedidos de compra en borrador del mismo proveedor y misma campaña en uno solo (el más reciente), moviendo todas las líneas a él y eliminando los absorbidos. Se ejecuta desde la vista lista de `purchase.order` mediante acción contextual.

---

## 2. Restricciones de fusión

| Condición requerida | Comportamiento si no se cumple |
|---|---|
| Al menos 2 POs seleccionados | Error en wizard: "Selecciona al menos 2 pedidos de compra." |
| Todos en estado `draft` | Error: "Solo se pueden fusionar pedidos en estado borrador." |
| Todos con el mismo `partner_id` | Error: "Todos los pedidos deben ser del mismo proveedor." |
| Todos con la misma `shoes_campaign_id` (incluyendo todos sin campaña) | Error: "Todos los pedidos deben tener la misma campaña." |

---

## 3. PO superviviente

El PO con el `id` más alto (el creado más recientemente) absorbe las líneas de todos los demás.

---

## 4. Resolución de campos de cabecera

| Campo | Regla |
|---|---|
| `partner_id` | Del superviviente (todos iguales) |
| `shoes_campaign_id` | Del superviviente (todos iguales) |
| `currency_id` | Del superviviente |
| `company_id` | Del superviviente |
| `date_planned` | Máximo de todas las fechas válidas (no nulas) |
| `partner_ref` | Del superviviente |
| `notes` | Concatenación de las notas de todos los POs separadas por `\n` (solo las no vacías) |

---

## 5. Estructura de archivos

**Nuevos:**
```
shoes_purchase/
├── data/
│   └── purchase_merge_server_action.xml
├── wizard/
│   ├── purchase_merge_wizard.py
│   └── purchase_merge_wizard_views.xml
```

**Modificados:**
```
shoes_purchase/__manifest__.py         — añade 3 nuevos archivos en data
shoes_purchase/wizard/__init__.py      — añade import purchase_merge_wizard
shoes_purchase/models/purchase_order.py — añade action_open_merge_wizard
```

---

## 6. Modelo `purchase.merge.wizard` (TransientModel)

### 6.1 Campos

| Campo | Tipo | Atributos | Descripción |
|---|---|---|---|
| `purchase_order_ids` | Many2many → `purchase.order` | readonly | POs seleccionados |
| `survivor_id` | Many2one → `purchase.order` | compute, no-store | PO con id más alto |
| `merged_notes` | Text | compute, no-store | Notas concatenadas |
| `can_merge` | Boolean | compute, no-store | True si validaciones OK |
| `validation_error` | Char | compute, no-store | Mensaje de error o False |

### 6.2 Método `action_merge()`

```
1. Re-validar (defensa en profundidad) → UserError si falla
2. to_absorb = purchase_order_ids - survivor_id
3. to_absorb.order_line.write({'order_id': survivor_id.id})
4. survivor_id.date_planned = max(fechas válidas de todos los POs)
5. survivor_id.notes = merged_notes
6. Para cada po in to_absorb:
       po._delete_unused_po_lots()
   to_absorb.unlink()
7. survivor_id.create_lots_for_purchase_order()
8. Retornar ir.actions.act_window abriendo survivor_id en formulario
```

**Lotes de SO:** siguen automáticamente a las líneas vía `sale_line_id.order_id` — sin acción adicional.

**Por qué `to_absorb.order_line.write({'order_id': ...})` no rompe validaciones:**
- `shoes_shippingmark` solo lanza UserError al cambiar `product_qty`. ✓
- `purchase_lot_preassignment` solo dispara `create_lots_for_purchase_order()` al cambiar `product_qty`. El `action_merge` lo llama explícitamente. ✓

---

## 7. Acción en `purchase.order`

```python
def action_open_merge_wizard(self):
    # self = registros seleccionados desde la lista
    return {
        'name': 'Fusionar pedidos de compra',
        'type': 'ir.actions.act_window',
        'res_model': 'purchase.merge.wizard',
        'view_mode': 'form',
        'target': 'new',
        'context': {'default_purchase_order_ids': self.ids},
    }
```

---

## 8. Server action

`ir.actions.server` de tipo `code` enlazada a `purchase.order` con `binding_view_types = list`:

```python
action = records.action_open_merge_wizard()
```

---

## 9. Vista del wizard

- Cabecera: lista readonly de POs a fusionar (nombre, proveedor, campaña, nº líneas).
- Sección info: PO superviviente destacado, `date_planned` resultante, notas fusionadas.
- Alerta de error inline si `not can_merge`.
- Footer: botón **"Fusionar"** (deshabilitado si `not can_merge`) y **"Cancelar"**.
