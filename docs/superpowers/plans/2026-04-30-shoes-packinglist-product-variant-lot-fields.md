# shoes_packinglist: product.product + stock.lot fields Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move `width_length_high` from `product.template` to `product.product`, and add gross weight / net weight / volume / width_length_high as independent fields on `stock.lot`, written from the packing list update process.

**Architecture:** Three independent changes — model/view for `product.product`, model/view for `stock.lot`, and updated logic in `_update_product_weights_from_packing_list` to write `width_length_high` to `product.product` (assortment only) and all four fields to the matched `stock.lot` per line.

**Tech Stack:** Odoo 18, Python, XML views. Module `product_net_weight` already stores `weight`/`net_weight` at `product.product` level with computed delegates on `product.template`.

---

## File Map

| Action  | File |
|---------|------|
| Rename  | `models/product_template.py` → `models/product_product.py` |
| Update  | `models/__init__.py` |
| Rename  | `views/product_template_views.xml` → `views/product_product_views.xml` |
| Create  | `models/stock_lot.py` |
| Create  | `views/stock_lot_views.xml` |
| Update  | `models/purchase_container.py` |
| Update  | `__manifest__.py` |

---

## Task 1: Move `width_length_high` to `product.product`

**Files:**
- Rename: `shoes_packinglist/models/product_template.py` → `shoes_packinglist/models/product_product.py`
- Modify: `shoes_packinglist/models/__init__.py`
- Rename: `shoes_packinglist/views/product_template_views.xml` → `shoes_packinglist/views/product_product_views.xml`
- Modify: `shoes_packinglist/__manifest__.py`
- Test: `shoes_packinglist/tests/test_product_product.py` (new)

- [ ] **Step 1: Write failing test**

Create `shoes_packinglist/tests/test_product_product.py`:

```python
from odoo.tests.common import TransactionCase


class TestProductProductFields(TransactionCase):

    def test_width_length_high_on_product_product(self):
        product = self.env["product.product"].create(
            {"name": "Test Shoe", "type": "consu"}
        )
        product.write({"width_length_high": "25×30×50"})
        self.assertEqual(product.width_length_high, "25×30×50")

    def test_width_length_high_independent_per_variant(self):
        tmpl = self.env["product.template"].create(
            {
                "name": "Test Shoe Multi",
                "type": "consu",
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": self.env["product.attribute"]
                            .create({"name": "Size"})
                            .id,
                            "value_ids": [
                                (
                                    0,
                                    0,
                                    {"name": "36"},
                                ),
                                (
                                    0,
                                    0,
                                    {"name": "37"},
                                ),
                            ],
                        },
                    )
                ],
            }
        )
        v1, v2 = tmpl.product_variant_ids
        v1.write({"width_length_high": "25×30×50"})
        v2.write({"width_length_high": "26×31×51"})
        self.assertEqual(v1.width_length_high, "25×30×50")
        self.assertEqual(v2.width_length_high, "26×31×51")
```

- [ ] **Step 2: Add test to `tests/__init__.py`**

`shoes_packinglist/tests/__init__.py` currently imports test modules. Add:

```python
from . import test_product_product
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/acanovas/pycharmprojects/dev18
python -m pytest shoes_packinglist/tests/test_product_product.py -v 2>&1 | head -30
```

Expected: `AttributeError` or `KeyError` — field does not exist on `product.product` yet.

- [ ] **Step 4: Rename model file and change `_inherit`**

Delete `shoes_packinglist/models/product_template.py` and create `shoes_packinglist/models/product_product.py`:

```python
from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    width_length_high = fields.Char(string="W×L×H (cm)")
```

- [ ] **Step 5: Update `models/__init__.py`**

```python
from . import product_product
from . import purchase_container_line
from . import purchase_container
```

- [ ] **Step 6: Update the product form view**

Delete `shoes_packinglist/views/product_template_views.xml` and create `shoes_packinglist/views/product_product_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="product_product_form_view_packinglist" model="ir.ui.view">
        <field name="name">product.product.form.packinglist</field>
        <field name="model">product.product</field>
        <field name="inherit_id" ref="product.product_variant_easy_edit_view"/>
        <field name="arch" type="xml">
            <xpath expr="//div[@name='volume']" position="after">
                <label for="width_length_high"/>
                <div class="o_row">
                    <field name="width_length_high"/>
                </div>
            </xpath>
        </field>
    </record>

</odoo>
```

- [ ] **Step 7: Update `__manifest__.py`**

```python
{
    "name": "Shoes Packing List",
    "summary": "Import container packing lists and match stock pickings.",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "Ingenieriacloud",
    "depends": [
        "purchase_container",
        "stock",
        "account",
        "product_net_weight",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/packing_list_warning_wizard_views.xml",
        "wizard/container_validate_wizard_views.xml",
        "views/product_product_views.xml",
        "views/purchase_container_line_views.xml",
        "views/purchase_container_views.xml",
    ],
}
```

- [ ] **Step 8: Run tests to verify they pass**

```bash
cd /Users/acanovas/pycharmprojects/dev18
python -m pytest shoes_packinglist/tests/test_product_product.py -v
```

Expected: Both tests PASS.

- [ ] **Step 9: Commit**

```bash
git add shoes_packinglist/models/product_product.py \
        shoes_packinglist/models/__init__.py \
        shoes_packinglist/views/product_product_views.xml \
        shoes_packinglist/__manifest__.py
git rm shoes_packinglist/models/product_template.py \
       shoes_packinglist/views/product_template_views.xml
git add shoes_packinglist/tests/test_product_product.py \
        shoes_packinglist/tests/__init__.py
git commit -m "feat(shoes_packinglist): move width_length_high to product.product"
```

---

## Task 2: Add packing list fields to `stock.lot`

**Files:**
- Create: `shoes_packinglist/models/stock_lot.py`
- Create: `shoes_packinglist/views/stock_lot_views.xml`
- Modify: `shoes_packinglist/__manifest__.py`
- Test: `shoes_packinglist/tests/test_stock_lot.py` (new)

- [ ] **Step 1: Write failing test**

Create `shoes_packinglist/tests/test_stock_lot.py`:

```python
from odoo.tests.common import TransactionCase


class TestStockLotPackingListFields(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env["product.product"].create(
            {"name": "Test Shoe Lot", "type": "consu", "tracking": "lot"}
        )
        self.lot = self.env["stock.lot"].create(
            {
                "name": "LOT_TEST",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )

    def test_lot_has_weight_field(self):
        self.lot.write({"weight": 5.0})
        self.assertAlmostEqual(self.lot.weight, 5.0)

    def test_lot_has_net_weight_field(self):
        self.lot.write({"net_weight": 4.5})
        self.assertAlmostEqual(self.lot.net_weight, 4.5)

    def test_lot_has_volume_field(self):
        self.lot.write({"volume": 0.5})
        self.assertAlmostEqual(self.lot.volume, 0.5)

    def test_lot_has_width_length_high_field(self):
        self.lot.write({"width_length_high": "25×30×50"})
        self.assertEqual(self.lot.width_length_high, "25×30×50")

    def test_lot_fields_independent_from_product(self):
        self.lot.write({"weight": 5.0, "net_weight": 4.5, "volume": 0.5, "width_length_high": "25×30×50"})
        self.product.write({"weight": 99.0})
        self.assertAlmostEqual(self.lot.weight, 5.0)
```

- [ ] **Step 2: Add test to `tests/__init__.py`**

```python
from . import test_product_product
from . import test_stock_lot
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
cd /Users/acanovas/pycharmprojects/dev18
python -m pytest shoes_packinglist/tests/test_stock_lot.py -v 2>&1 | head -30
```

Expected: `AttributeError` — fields do not exist on `stock.lot` yet.

- [ ] **Step 4: Create `models/stock_lot.py`**

```python
from odoo import fields, models


class StockLot(models.Model):
    _inherit = "stock.lot"

    weight = fields.Float(string="Gross Weight", digits="Stock Weight")
    net_weight = fields.Float(string="Net Weight", digits="Stock Weight")
    volume = fields.Float(string="Volume", digits="Volume")
    width_length_high = fields.Char(string="W×L×H (cm)")
```

- [ ] **Step 5: Update `models/__init__.py`**

```python
from . import product_product
from . import stock_lot
from . import purchase_container_line
from . import purchase_container
```

- [ ] **Step 6: Create `views/stock_lot_views.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>

    <record id="stock_lot_form_view_packinglist" model="ir.ui.view">
        <field name="name">stock.lot.form.packinglist</field>
        <field name="model">stock.lot</field>
        <field name="inherit_id" ref="stock.view_production_lot_form"/>
        <field name="arch" type="xml">
            <xpath expr="//sheet" position="inside">
                <group string="Packing List Data">
                    <group>
                        <field name="weight"/>
                        <field name="net_weight"/>
                    </group>
                    <group>
                        <field name="volume"/>
                        <field name="width_length_high"/>
                    </group>
                </group>
            </xpath>
        </field>
    </record>

</odoo>
```

- [ ] **Step 7: Update `__manifest__.py`**

```python
{
    "name": "Shoes Packing List",
    "summary": "Import container packing lists and match stock pickings.",
    "version": "18.0.1.0.0",
    "license": "LGPL-3",
    "author": "Ingenieriacloud",
    "depends": [
        "purchase_container",
        "stock",
        "account",
        "product_net_weight",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/packing_list_warning_wizard_views.xml",
        "wizard/container_validate_wizard_views.xml",
        "views/product_product_views.xml",
        "views/stock_lot_views.xml",
        "views/purchase_container_line_views.xml",
        "views/purchase_container_views.xml",
    ],
}
```

- [ ] **Step 8: Run tests to verify they pass**

```bash
cd /Users/acanovas/pycharmprojects/dev18
python -m pytest shoes_packinglist/tests/test_stock_lot.py -v
```

Expected: All 5 tests PASS.

- [ ] **Step 9: Commit**

```bash
git add shoes_packinglist/models/stock_lot.py \
        shoes_packinglist/models/__init__.py \
        shoes_packinglist/views/stock_lot_views.xml \
        shoes_packinglist/__manifest__.py \
        shoes_packinglist/tests/test_stock_lot.py \
        shoes_packinglist/tests/__init__.py
git commit -m "feat(shoes_packinglist): add packing list fields to stock.lot"
```

---

## Task 3: Update `_update_product_weights_from_packing_list`

**Files:**
- Modify: `shoes_packinglist/models/purchase_container.py`
- Test: `shoes_packinglist/tests/test_packing_list_update.py` (extend existing)

Three changes in `_update_product_weights_from_packing_list`:
1. Write `width_length_high` to `product.product` (assortment only) instead of `product.template`
2. Remove `width_length_high` from pair template writes
3. Add lot write per line (weight, net_weight, volume, width_length_high)

- [ ] **Step 1: Write failing tests**

Add a new test class at the end of `shoes_packinglist/tests/test_packing_list_update.py`:

```python
class TestProductAndLotUpdate(PackingListCommon):
    """Tests for _update_product_weights_from_packing_list."""

    def _run_update_with_line(self, width=25.0, length=30.0, high=50.0,
                               gross=5.0, net=4.5, volume=0.5):
        """Helper: full update cycle with a single matched line."""
        picking, _ = self._make_incoming_picking([self.lot1])
        container = self.env["purchase.container"].create(
            {"code": "CONT_UPDATE", "shipping_agent_id": self.partner.id}
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOT001",
                "width": width,
                "length": length,
                "high": high,
                "assortment_gross_weight": gross,
                "assortment_net_weight": net,
                "volume": volume,
            }
        )
        container.action_update_from_packing_list()
        return container

    def test_width_length_high_written_to_product_product(self):
        self._run_update_with_line()
        self.assertEqual(self.product.width_length_high, "25×30×50")

    def test_lot_weight_written_from_packing_list(self):
        self._run_update_with_line(gross=5.0)
        self.assertAlmostEqual(self.lot1.weight, 5.0)

    def test_lot_net_weight_written_from_packing_list(self):
        self._run_update_with_line(net=4.5)
        self.assertAlmostEqual(self.lot1.net_weight, 4.5)

    def test_lot_volume_written_from_packing_list(self):
        self._run_update_with_line(volume=0.5)
        self.assertAlmostEqual(self.lot1.volume, 0.5)

    def test_lot_width_length_high_written_from_packing_list(self):
        self._run_update_with_line(width=25.0, length=30.0, high=50.0)
        self.assertEqual(self.lot1.width_length_high, "25×30×50")

    def test_lot_fields_not_written_when_no_dimensions(self):
        self._run_update_with_line(width=0.0, length=0.0, high=0.0)
        self.assertFalse(self.lot1.width_length_high)

    def test_two_lines_update_two_lots_independently(self):
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2])
        container = self.env["purchase.container"].create(
            {"code": "CONT_TWO", "shipping_agent_id": self.partner.id}
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOT001",
                "assortment_gross_weight": 5.0,
                "assortment_net_weight": 4.5,
                "volume": 0.5,
                "width": 25.0,
                "length": 30.0,
                "high": 50.0,
            }
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOT002",
                "assortment_gross_weight": 6.0,
                "assortment_net_weight": 5.5,
                "volume": 0.6,
                "width": 26.0,
                "length": 31.0,
                "high": 51.0,
            }
        )
        container.action_update_from_packing_list()
        self.assertAlmostEqual(self.lot1.weight, 5.0)
        self.assertAlmostEqual(self.lot2.weight, 6.0)
        self.assertEqual(self.lot1.width_length_high, "25×30×50")
        self.assertEqual(self.lot2.width_length_high, "26×31×51")
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/acanovas/pycharmprojects/dev18
python -m pytest shoes_packinglist/tests/test_packing_list_update.py::TestProductAndLotUpdate -v 2>&1 | head -50
```

Expected: Tests fail — `width_length_high` still written to template, lot fields not populated.

- [ ] **Step 3: Update `_update_product_weights_from_packing_list` in `purchase_container.py`**

Replace the entire method:

```python
def _update_product_weights_from_packing_list(self, processed_lines):
    """
    Update weight, net_weight, volume on product templates and width_length_high
    on the assortment product.product. Also writes all four fields to the matched
    stock.lot for each line (no deduplication — each line has its own lot).

    For assortment products: writes assortment_gross_weight, assortment_net_weight,
    volume to product.template; width_length_high to product.product.
    For pair products (linked via product_tmpl_single_id): writes pair_gross_weight,
    pair_net_weight, volume / pairs to product.template only.
    Deduplicates product writes by product.id so each product is written once.
    """
    seen_product_ids = set()
    for line in processed_lines:
        if not line.move_id:
            continue
        product = line.move_id.product_id
        if not product:
            continue

        # Build W×L×H string from dimension fields
        wlh_parts = [line.width, line.length, line.high]
        if any(wlh_parts):
            width_length_high = "×".join(
                str(int(v) if v == int(v) else v) for v in wlh_parts
            )
        else:
            width_length_high = False

        # Update lot fields (per line, no deduplication)
        lot = self.env["stock.lot"].search(
            [("name", "=", line.lot), ("company_id", "=", self.env.company.id)],
            limit=1,
        )
        if lot:
            lot_vals = {
                "weight": line.assortment_gross_weight,
                "net_weight": line.assortment_net_weight,
                "volume": line.volume,
            }
            if width_length_high:
                lot_vals["width_length_high"] = width_length_high
            lot.write(lot_vals)

        # Deduplicate product/template writes by product.id
        if product.id in seen_product_ids:
            continue
        seen_product_ids.add(product.id)

        tmpl = product.product_tmpl_id

        # Update assortment template (weight/net_weight/volume)
        assortment_vals = {
            "weight": line.assortment_gross_weight,
            "net_weight": line.assortment_net_weight,
            "volume": line.volume,
        }
        tmpl.write(assortment_vals)

        # Update assortment product.product (width_length_high only)
        if width_length_high:
            product.write({"width_length_high": width_length_high})

        # Update pair products (template only, no width_length_high)
        pair_tmpl = getattr(product, "product_tmpl_single_id", False)
        if not pair_tmpl:
            continue
        pairs = line.pairs or 1.0
        pair_vals = {
            "weight": line.pair_gross_weight,
            "net_weight": line.pair_net_weight,
            "volume": line.volume / pairs,
        }
        pair_tmpl.write(pair_vals)
```

- [ ] **Step 4: Run all tests to verify they pass**

```bash
cd /Users/acanovas/pycharmprojects/dev18
python -m pytest shoes_packinglist/tests/ -v
```

Expected: All tests PASS, including the full existing suite.

- [ ] **Step 5: Commit**

```bash
git add shoes_packinglist/models/purchase_container.py \
        shoes_packinglist/tests/test_packing_list_update.py
git commit -m "feat(shoes_packinglist): write width_length_high to product.product and fields to stock.lot"
```
