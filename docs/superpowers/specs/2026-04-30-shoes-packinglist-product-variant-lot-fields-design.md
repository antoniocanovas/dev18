# Design: Move width_length_high to product.product + stock.lot fields

**Date:** 2026-04-30  
**Module:** shoes_packinglist

---

## Context

The `width_length_high` field is currently on `product.template`, but it represents the box dimensions of a specific assortment (box), which can differ per product variant. It must move to `product.product`. Additionally, the fields saved to the product from the packing list (gross weight, net weight, volume, and dimensions) can vary per lot, so they must also be stored independently on `stock.lot`.

---

## Changes

### 1. Move `width_length_high` from `product.template` to `product.product`

**File changes:**
- Rename `models/product_template.py` → `models/product_product.py`
- Change `_inherit = "product.template"` → `_inherit = "product.product"`
- Field definition unchanged: `width_length_high = fields.Char(string="W×L×H (cm)")`
- Update `models/__init__.py` to import `product_product` instead of `product_template`

**Scope:** Only the assortment product (`product.product`) receives `width_length_high`. Pair products do not — dimensions refer only to the assortment box (for customs purposes).

---

### 2. Update the product form view

**File:** `views/product_template_views.xml` → rename to `views/product_product_views.xml`

- Inherit from `product.product_variant_easy_edit_view` (Odoo 18 product.product form view)
- XPath targets `//div[@name='volume']` (same anchor, exists in the variant form)
- Render `width_length_high` after the volume div

**Manifest:** update `data` list to reference `views/product_product_views.xml`

---

### 3. Add fields to `stock.lot`

**New file:** `models/stock_lot.py`

```
_inherit = "stock.lot"

weight          Float  "Gross Weight"   digits="Stock Weight"
net_weight      Float  "Net Weight"     digits="Stock Weight"
volume          Float  "Volume"         digits="Volume"
width_length_high  Char  "W×L×H (cm)"
```

These are independent fields with no relation to the product fields. They are populated from the packing list update process.

**New file:** `views/stock_lot_views.xml`

- Inherit from `stock.stock_lot_form_view`
- Add a group "Packing List Data" with the 4 fields after the existing fields

**Manifest:** add `models/stock_lot.py` and `views/stock_lot_views.xml`

**Security:** add `stock.lot` to `security/ir.model.access.csv` if not already present (check at implementation time — Odoo base likely already grants access).

---

### 4. Update `_update_product_weights_from_packing_list` in `purchase_container.py`

**Current behavior:**
- Deduplicates by `tmpl.id` (product.template)
- Writes `weight`, `net_weight`, `volume`, `width_length_high` to assortment `tmpl`
- Writes `weight`, `net_weight`, `volume`, `width_length_high` to `pair_tmpl`

**New behavior:**

#### Assortment product
- Write `weight`, `net_weight`, `volume` to `tmpl` (product.template) — unchanged
- Write `width_length_high` to `product` (product.product) — changed from tmpl to product

#### Pair product  
- Write `weight`, `net_weight`, `volume` to `pair_tmpl` (product.template) — unchanged
- Do NOT write `width_length_high` to pair — removed

#### Lot update (new)
- Deduplication remains by template for product writes
- Lot writes are per-line (each line has its own lot, no deduplication needed)
- After the product write block, look up the `stock.lot` by `line.lot` name
- Write to the lot: `weight` (assortment_gross_weight), `net_weight` (assortment_net_weight), `volume`, `width_length_high`
- If no lot found, skip silently (lot lookup already exists in `_assign_lots_to_moves`)

**Field mapping from packing list line to lot:**

| `stock.lot` field  | Source (`purchase.container.line` field) |
|--------------------|------------------------------------------|
| `weight`           | `assortment_gross_weight`               |
| `net_weight`       | `assortment_net_weight`                 |
| `volume`           | `volume`                                |
| `width_length_high`| computed W×L×H string (same as product) |

---

## File Summary

| Action  | File                                   |
|---------|----------------------------------------|
| Rename  | `models/product_template.py` → `models/product_product.py` |
| Update  | `models/__init__.py`                  |
| Rename  | `views/product_template_views.xml` → `views/product_product_views.xml` |
| Create  | `models/stock_lot.py`                 |
| Create  | `views/stock_lot_views.xml`           |
| Update  | `models/purchase_container.py`        |
| Update  | `__manifest__.py`                     |
| Check   | `security/ir.model.access.csv`        |

---

## Out of Scope

- No changes to `purchase.container.line` model
- No changes to lot assignment logic (`_assign_lots_to_moves`)
- No computed/related fields between lot and product
- No migration script needed (new fields start empty; existing `width_length_high` data on product.template will be lost — acceptable since the field is newly introduced)
