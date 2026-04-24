# shoes_packinglist Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the `shoes_packinglist` Odoo 18 module to import container packing lists, match lot-level stock moves, split partial pickings, and update container logistics metrics.

**Architecture:** New module that inherits `purchase.container` (no modifications to source module) adding a `purchase.container.line` o2m model for spreadsheet import. A button "Update" executes lot matching, splits partial incoming pickings into a container picking + backorder, and recalculates container weight/volume/package count. A transient wizard handles missing-lot confirmation.

**Tech Stack:** Odoo 18, Python 3.12, `purchase_container` (OCA), `stock`, `purchase_stock`.

---

## File Map

| File | Role |
|---|---|
| `shoes_packinglist/__init__.py` | Module root |
| `shoes_packinglist/__manifest__.py` | Module metadata |
| `shoes_packinglist/models/__init__.py` | Models package |
| `shoes_packinglist/models/purchase_container_line.py` | New `purchase.container.line` model |
| `shoes_packinglist/models/purchase_container.py` | Inherits `purchase.container`, adds o2m + Update logic |
| `shoes_packinglist/wizard/__init__.py` | Wizard package |
| `shoes_packinglist/wizard/packing_list_warning_wizard.py` | Unmatched-lots wizard |
| `shoes_packinglist/views/purchase_container_line_views.xml` | List/form views for container lines |
| `shoes_packinglist/views/purchase_container_views.xml` | XPath extension of existing container form |
| `shoes_packinglist/views/packing_list_warning_wizard_views.xml` | Wizard form view |
| `shoes_packinglist/security/ir.model.access.csv` | ACLs |
| `shoes_packinglist/tests/__init__.py` | Tests package |
| `shoes_packinglist/tests/common.py` | Shared test fixtures |
| `shoes_packinglist/tests/test_container_line.py` | Tests: char cleaning |
| `shoes_packinglist/tests/test_packing_list_update.py` | Tests: Update button logic |

---

## Task 1: Module Scaffold

**Files:**
- Create: `shoes_packinglist/__init__.py`
- Create: `shoes_packinglist/__manifest__.py`
- Create: `shoes_packinglist/models/__init__.py`
- Create: `shoes_packinglist/wizard/__init__.py`
- Create: `shoes_packinglist/tests/__init__.py`
- Create: `shoes_packinglist/security/ir.model.access.csv`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p shoes_packinglist/models shoes_packinglist/wizard \
         shoes_packinglist/views shoes_packinglist/security \
         shoes_packinglist/tests
```

- [ ] **Step 2: Create `shoes_packinglist/__init__.py`**

```python
from . import models, wizard
```

- [ ] **Step 3: Create `shoes_packinglist/__manifest__.py`**

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
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizard/packing_list_warning_wizard_views.xml",
        "views/purchase_container_line_views.xml",
        "views/purchase_container_views.xml",
    ],
}
```

- [ ] **Step 4: Create `shoes_packinglist/models/__init__.py`**

```python
from . import purchase_container_line
from . import purchase_container
```

- [ ] **Step 5: Create `shoes_packinglist/wizard/__init__.py`**

```python
from . import packing_list_warning_wizard
```

- [ ] **Step 6: Create `shoes_packinglist/tests/__init__.py`**

```python
from . import test_container_line
from . import test_packing_list_update
```

- [ ] **Step 7: Create `shoes_packinglist/security/ir.model.access.csv`**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_purchase_container_line_user,purchase.container.line user,model_purchase_container_line,purchase.group_purchase_user,1,1,1,1
access_purchase_container_line_readonly,purchase.container.line readonly,model_purchase_container_line,account.group_account_readonly,1,0,0,0
access_purchase_container_line_invoice,purchase.container.line invoice,model_purchase_container_line,account.group_account_invoice,1,1,0,0
access_packing_list_warning_wizard,packing.list.warning.wizard,model_packing_list_warning_wizard,purchase.group_purchase_user,1,1,1,1
access_packing_list_warning_line,packing.list.warning.line,model_packing_list_warning_line,purchase.group_purchase_user,1,1,1,1
```

- [ ] **Step 8: Create placeholder model files so the module loads**

`shoes_packinglist/models/purchase_container_line.py`:
```python
from odoo import fields, models
```

`shoes_packinglist/models/purchase_container.py`:
```python
from odoo import fields, models
```

`shoes_packinglist/wizard/packing_list_warning_wizard.py`:
```python
from odoo import fields, models
```

- [ ] **Step 9: Create placeholder view XML files (required for manifest)**

`shoes_packinglist/views/purchase_container_line_views.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo/>
```

`shoes_packinglist/views/purchase_container_views.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo/>
```

`shoes_packinglist/wizard/packing_list_warning_wizard_views.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo/>
```

- [ ] **Step 10: Verify module loads in Odoo**

```bash
python odoo-bin -d <db> -u shoes_packinglist --stop-after-init 2>&1 | tail -20
```
Expected: no `ImportError` or `KeyError` in output.

- [ ] **Step 11: Commit**

```bash
git add shoes_packinglist/
git commit -m "feat(shoes_packinglist): add module scaffold"
```

---

## Task 2: `purchase.container.line` Model + Char Cleaning Tests

**Files:**
- Modify: `shoes_packinglist/models/purchase_container_line.py`
- Create: `shoes_packinglist/tests/common.py`
- Create: `shoes_packinglist/tests/test_container_line.py`

- [ ] **Step 1: Create shared test fixtures `shoes_packinglist/tests/common.py`**

```python
from odoo.tests.common import TransactionCase


class PackingListCommon(TransactionCase):
    """Shared fixtures for shoes_packinglist tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Shipping agent partner
        cls.partner = cls.env["res.partner"].create({"name": "Test Shipping Agent"})

        # Product with lot tracking
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Shoe Model",
                "type": "consu",
                "tracking": "lot",
            }
        )

        # Lots
        cls.lot1 = cls.env["stock.lot"].create(
            {
                "name": "LOT001",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.lot2 = cls.env["stock.lot"].create(
            {
                "name": "LOT002",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.lot3 = cls.env["stock.lot"].create(
            {
                "name": "LOT003",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )

        # Warehouse / picking type
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.supplier_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_loc = cls.warehouse.lot_stock_id

        # Container (no lines yet)
        cls.container = cls.env["purchase.container"].create(
            {
                "code": "CONT001",
                "shipping_agent_id": cls.partner.id,
            }
        )

    def _make_incoming_picking(self, lots):
        """
        Create a confirmed incoming picking with one move per lot.
        Returns (picking, {lot: move_line}) for easy access in tests.
        """
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "picking_id": picking.id,
                "product_id": self.product.id,
                "product_uom_qty": float(len(lots)),
                "product_uom": self.product.uom_id.id,
                "location_id": self.supplier_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        picking.action_confirm()
        move_lines = {}
        for lot in lots:
            ml = self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": picking.id,
                    "product_id": self.product.id,
                    "lot_id": lot.id,
                    "quantity": 1.0,
                    "product_uom_id": self.product.uom_id.id,
                    "location_id": self.supplier_loc.id,
                    "location_dest_id": self.stock_loc.id,
                }
            )
            move_lines[lot.name] = ml
        return picking, move_lines
```

- [ ] **Step 2: Write failing tests for char field cleaning**

`shoes_packinglist/tests/test_container_line.py`:
```python
from .common import PackingListCommon


class TestContainerLineCharCleaning(PackingListCommon):

    def test_lot_stripped_on_create(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "  LOT001  "}
        )
        self.assertEqual(line.lot, "LOT001")

    def test_tabulations_removed_on_create(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "name": "\tShoe Name\t"}
        )
        self.assertEqual(line.name, "Shoe Name")

    def test_all_char_fields_stripped_on_create(self):
        line = self.env["purchase.container.line"].create(
            {
                "container_id": self.container.id,
                "shoes_campaign": " Camp ",
                "name": " Name ",
                "color": " Black ",
                "purchase_order": " PO001 ",
                "assortment": " Assort ",
                "lot": " LOT001 ",
                "shippingmark": " SM01 ",
            }
        )
        self.assertEqual(line.shoes_campaign, "Camp")
        self.assertEqual(line.name, "Name")
        self.assertEqual(line.color, "Black")
        self.assertEqual(line.purchase_order, "PO001")
        self.assertEqual(line.assortment, "Assort")
        self.assertEqual(line.lot, "LOT001")
        self.assertEqual(line.shippingmark, "SM01")

    def test_char_fields_stripped_on_write(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        line.write({"lot": "  LOT002  ", "name": "  Shoe  "})
        self.assertEqual(line.lot, "LOT002")
        self.assertEqual(line.name, "Shoe")

    def test_empty_char_fields_not_modified(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001", "name": False}
        )
        self.assertFalse(line.name)

    def test_numeric_fields_not_affected(self):
        line = self.env["purchase.container.line"].create(
            {
                "container_id": self.container.id,
                "lot": "LOT001",
                "pairs": 12.0,
                "assortment_gross_weight": 5.5,
            }
        )
        self.assertEqual(line.pairs, 12.0)
        self.assertEqual(line.assortment_gross_weight, 5.5)
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist.TestContainerLineCharCleaning 2>&1 | tail -30
```
Expected: `ERROR` — model `purchase.container.line` does not exist yet.

- [ ] **Step 4: Implement `purchase.container.line` model**

`shoes_packinglist/models/purchase_container_line.py`:
```python
from odoo import api, fields, models

_CHAR_FIELDS = [
    "shoes_campaign",
    "name",
    "color",
    "purchase_order",
    "assortment",
    "lot",
    "shippingmark",
]


class PurchaseContainerLine(models.Model):
    _name = "purchase.container.line"
    _description = "Purchase Container Packing List Line"
    _order = "container_id, id"
    _rec_name = "lot"

    container_id = fields.Many2one(
        "purchase.container",
        string="Container",
        required=True,
        ondelete="cascade",
        index=True,
    )
    shoes_campaign = fields.Char(string="Campaign")
    name = fields.Char(string="Product Ref.")
    color = fields.Char(string="Color")
    pairs = fields.Float(string="Pairs", digits="Product Unit of Measure")
    purchase_order = fields.Char(string="Purchase Order")
    assortment = fields.Char(string="Assortment")
    lot = fields.Char(string="Lot")
    volume = fields.Float(string="Volume", digits="Volume")
    pair_net_weight = fields.Float(string="Pair Net Weight", digits="Stock Weight")
    pair_gross_weight = fields.Float(string="Pair Gross Weight", digits="Stock Weight")
    assortment_net_weight = fields.Float(
        string="Assortment Net Weight", digits="Stock Weight"
    )
    assortment_gross_weight = fields.Float(
        string="Assortment Gross Weight", digits="Stock Weight"
    )
    shippingmark = fields.Char(string="Shipping Mark")
    high = fields.Float(string="High", digits="Volume")
    width = fields.Float(string="Width", digits="Volume")
    length = fields.Float(string="Length", digits="Volume")
    move_id = fields.Many2one(
        "stock.move",
        string="Stock Move",
        readonly=True,
        index=True,
        copy=False,
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            _clean_char_fields(vals)
        return super().create(vals_list)

    def write(self, vals):
        _clean_char_fields(vals)
        return super().write(vals)


def _clean_char_fields(vals):
    """Strip leading/trailing whitespace and tabs from all Char fields."""
    for field in _CHAR_FIELDS:
        if vals.get(field):
            vals[field] = vals[field].strip()
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist.TestContainerLineCharCleaning 2>&1 | tail -30
```
Expected: `OK` — 6 tests pass.

- [ ] **Step 6: Commit**

```bash
git add shoes_packinglist/models/purchase_container_line.py \
        shoes_packinglist/tests/common.py \
        shoes_packinglist/tests/test_container_line.py
git commit -m "feat(shoes_packinglist): add purchase.container.line model with char cleaning"
```

---

## Task 3: `purchase.container` Inheritance — o2m Field

**Files:**
- Modify: `shoes_packinglist/models/purchase_container.py`
- Modify: `shoes_packinglist/tests/test_container_line.py` (add one test)

- [ ] **Step 1: Add test for o2m field existence**

Append to `shoes_packinglist/tests/test_container_line.py`:
```python
class TestContainerO2M(PackingListCommon):

    def test_container_has_container_line_ids(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        self.assertIn(line, self.container.container_line_ids)

    def test_line_deleted_when_container_deleted(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        line_id = line.id
        self.container.unlink()
        self.assertFalse(self.env["purchase.container.line"].browse(line_id).exists())
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist.TestContainerO2M 2>&1 | tail -20
```
Expected: `ERROR` — `purchase.container` has no field `container_line_ids`.

- [ ] **Step 3: Implement inheritance**

`shoes_packinglist/models/purchase_container.py`:
```python
from odoo import fields, models


class PurchaseContainer(models.Model):
    _inherit = "purchase.container"

    container_line_ids = fields.One2many(
        "purchase.container.line",
        "container_id",
        string="Packing List",
        copy=False,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist.TestContainerO2M 2>&1 | tail -20
```
Expected: `OK` — 2 tests pass.

- [ ] **Step 5: Commit**

```bash
git add shoes_packinglist/models/purchase_container.py \
        shoes_packinglist/tests/test_container_line.py
git commit -m "feat(shoes_packinglist): add container_line_ids o2m to purchase.container"
```

---

## Task 4: `action_update_from_packing_list` — Validations

**Files:**
- Modify: `shoes_packinglist/models/purchase_container.py`
- Create: `shoes_packinglist/tests/test_packing_list_update.py`

- [ ] **Step 1: Write failing validation tests**

`shoes_packinglist/tests/test_packing_list_update.py`:
```python
from odoo.exceptions import UserError

from .common import PackingListCommon


class TestUpdateValidations(PackingListCommon):

    def test_error_when_no_shipping_agent(self):
        container = self.env["purchase.container"].create({"code": "CONT_NOAGENT"})
        self.env["purchase.container.line"].create(
            {"container_id": container.id, "lot": "LOT001"}
        )
        with self.assertRaises(UserError):
            container.action_update_from_packing_list()

    def test_error_when_no_packing_list_lines(self):
        container = self.env["purchase.container"].create(
            {"code": "CONT_NOLINES", "shipping_agent_id": self.partner.id}
        )
        with self.assertRaises(UserError):
            container.action_update_from_packing_list()

    def test_error_when_no_pending_pickings(self):
        # Container has agent + lines, but no incoming pickings for that partner
        other_partner = self.env["res.partner"].create({"name": "No Pickings Agent"})
        container = self.env["purchase.container"].create(
            {"code": "CONT_NOPICK", "shipping_agent_id": other_partner.id}
        )
        self.env["purchase.container.line"].create(
            {"container_id": container.id, "lot": "LOT001"}
        )
        with self.assertRaises(UserError):
            container.action_update_from_packing_list()
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist.TestUpdateValidations 2>&1 | tail -20
```
Expected: `ERROR` — method `action_update_from_packing_list` does not exist.

- [ ] **Step 3: Add validation logic to `purchase.container`**

Replace contents of `shoes_packinglist/models/purchase_container.py`:
```python
from odoo import _, fields, models
from odoo.exceptions import UserError


class PurchaseContainer(models.Model):
    _inherit = "purchase.container"

    container_line_ids = fields.One2many(
        "purchase.container.line",
        "container_id",
        string="Packing List",
        copy=False,
    )

    def action_update_from_packing_list(self):
        self.ensure_one()

        # --- Validation ---
        if not self.shipping_agent_id:
            raise UserError(
                _(
                    "Debe definir el agente de transporte (Shipping Agent) "
                    "del contenedor."
                )
            )
        if not self.container_line_ids:
            raise UserError(
                _(
                    "No hay líneas en el packing list. "
                    "Importe las líneas antes de actualizar."
                )
            )
        pending_pickings = self.env["stock.picking"].search(
            [
                ("partner_id", "=", self.shipping_agent_id.id),
                ("picking_type_id.code", "=", "incoming"),
                (
                    "state",
                    "in",
                    ["assigned", "waiting", "confirmed", "partially_available"],
                ),
            ]
        )
        if not pending_pickings:
            raise UserError(
                _(
                    'El proveedor "%s" no tiene albaranes de recepción pendientes.'
                )
                % self.shipping_agent_id.name
            )

        # --- Lot matching (to be implemented in Task 5) ---
        return True
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist.TestUpdateValidations 2>&1 | tail -20
```
Expected: `OK` — 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add shoes_packinglist/models/purchase_container.py \
        shoes_packinglist/tests/test_packing_list_update.py
git commit -m "feat(shoes_packinglist): add Update button validations"
```

---

## Task 5: Lot Matching + Unmatched Warning Wizard

**Files:**
- Modify: `shoes_packinglist/models/purchase_container.py`
- Create: `shoes_packinglist/wizard/packing_list_warning_wizard.py`
- Modify: `shoes_packinglist/tests/test_packing_list_update.py`

- [ ] **Step 1: Write failing tests for lot matching**

Append to `shoes_packinglist/tests/test_packing_list_update.py`:
```python
class TestLotMatching(PackingListCommon):

    def test_matched_lot_sets_move_id(self):
        picking, _ = self._make_incoming_picking([self.lot1])
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        self.container.action_update_from_packing_list()
        self.assertTrue(line.move_id)

    def test_unmatched_lot_returns_wizard(self):
        picking, _ = self._make_incoming_picking([self.lot1])
        self.env["purchase.container.line"].create(
            {
                "container_id": self.container.id,
                "lot": "LOT001",  # matched
            }
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": self.container.id,
                "lot": "LOTXXX",  # not in Odoo
            }
        )
        result = self.container.action_update_from_packing_list()
        self.assertEqual(result.get("res_model"), "packing.list.warning.wizard")

    def test_unmatched_lot_leaves_move_id_false(self):
        picking, _ = self._make_incoming_picking([self.lot1])
        unmatched_line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOTXXX"}
        )
        self.container.action_update_from_packing_list()
        self.assertFalse(unmatched_line.move_id)

    def test_lot_in_done_picking_not_matched(self):
        """Lots whose picking is already done must not be matched."""
        picking, _ = self._make_incoming_picking([self.lot1])
        picking.write({"state": "done"})  # force done for test
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        # Need another pending picking or we get UserError (no pending pickings)
        self._make_incoming_picking([self.lot2])
        self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT002"}
        )
        result = self.container.action_update_from_packing_list()
        # LOT001 was in a done picking → unmatched → wizard
        self.assertEqual(result.get("res_model"), "packing.list.warning.wizard")
        self.assertFalse(line.move_id)

    def test_all_matched_no_wizard(self):
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2])
        self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT002"}
        )
        result = self.container.action_update_from_packing_list()
        # No wizard — result is True (processing continues inline)
        self.assertNotIsInstance(result, dict)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist.TestLotMatching 2>&1 | tail -30
```
Expected: `ERROR` — lot matching not yet implemented.

- [ ] **Step 3: Create the warning wizard model**

`shoes_packinglist/wizard/packing_list_warning_wizard.py`:
```python
from odoo import fields, models


class PackingListWarningWizard(models.TransientModel):
    _name = "packing.list.warning.wizard"
    _description = "Packing List Unmatched Lots Warning"

    container_id = fields.Many2one("purchase.container", readonly=True)
    warning_line_ids = fields.One2many(
        "packing.list.warning.line",
        "wizard_id",
        string="Unmatched Lines",
        readonly=True,
    )

    def action_continue(self):
        """Process only lines that have move_id assigned."""
        self.ensure_one()
        self.container_id._process_packing_list_update()
        return {"type": "ir.actions.act_window_close"}

    def action_cancel(self):
        """Close without processing. Lines without move_id remain for review."""
        return {"type": "ir.actions.act_window_close"}


class PackingListWarningLine(models.TransientModel):
    _name = "packing.list.warning.line"
    _description = "Packing List Warning Line"

    wizard_id = fields.Many2one(
        "packing.list.warning.wizard", ondelete="cascade", index=True
    )
    lot = fields.Char(readonly=True)
    name = fields.Char(string="Product Ref.", readonly=True)
    purchase_order = fields.Char(readonly=True)
```

- [ ] **Step 4: Add lot matching to `action_update_from_packing_list`**

Replace `shoes_packinglist/models/purchase_container.py` with:
```python
from odoo import _, fields, models
from odoo.exceptions import UserError


class PurchaseContainer(models.Model):
    _inherit = "purchase.container"

    container_line_ids = fields.One2many(
        "purchase.container.line",
        "container_id",
        string="Packing List",
        copy=False,
    )

    def action_update_from_packing_list(self):
        self.ensure_one()

        # --- Validation ---
        if not self.shipping_agent_id:
            raise UserError(
                _(
                    "Debe definir el agente de transporte (Shipping Agent) "
                    "del contenedor."
                )
            )
        if not self.container_line_ids:
            raise UserError(
                _(
                    "No hay líneas en el packing list. "
                    "Importe las líneas antes de actualizar."
                )
            )
        pending_pickings = self.env["stock.picking"].search(
            [
                ("partner_id", "=", self.shipping_agent_id.id),
                ("picking_type_id.code", "=", "incoming"),
                (
                    "state",
                    "in",
                    ["assigned", "waiting", "confirmed", "partially_available"],
                ),
            ]
        )
        if not pending_pickings:
            raise UserError(
                _(
                    'El proveedor "%s" no tiene albaranes de recepción pendientes.'
                )
                % self.shipping_agent_id.name
            )

        # --- Lot matching ---
        # Reset previous matching
        self.container_line_ids.write({"move_id": False})

        unmatched = self.env["purchase.container.line"]
        for line in self.container_line_ids:
            if not line.lot:
                unmatched |= line
                continue
            lot = self.env["stock.lot"].search(
                [
                    ("name", "=", line.lot),
                    ("company_id", "=", self.env.company.id),
                ],
                limit=1,
            )
            if not lot:
                unmatched |= line
                continue
            move_line = self.env["stock.move.line"].search(
                [
                    ("lot_id", "=", lot.id),
                    ("picking_id", "in", pending_pickings.ids),
                    ("state", "not in", ["done", "cancel"]),
                ],
                limit=1,
            )
            if move_line:
                line.move_id = move_line.move_id
            else:
                unmatched |= line

        # --- Open wizard if there are unmatched lines ---
        if unmatched:
            wizard = self.env["packing.list.warning.wizard"].create(
                {
                    "container_id": self.id,
                    "warning_line_ids": [
                        (
                            0,
                            0,
                            {
                                "lot": ln.lot,
                                "name": ln.name,
                                "purchase_order": ln.purchase_order,
                            },
                        )
                        for ln in unmatched
                    ],
                }
            )
            return {
                "type": "ir.actions.act_window",
                "res_model": "packing.list.warning.wizard",
                "res_id": wizard.id,
                "view_mode": "form",
                "target": "new",
            }

        # --- All matched: proceed directly ---
        self._process_packing_list_update()
        return True

    def _process_packing_list_update(self):
        """Split pickings and update container metrics. Called after lot matching."""
        self.ensure_one()
        processed_lines = self.container_line_ids.filtered("move_id")
        if not processed_lines:
            return

        matched_lot_names = set(processed_lines.mapped("lot"))
        involved_pickings = processed_lines.mapped("move_id.picking_id")

        for picking in involved_pickings:
            all_mls = picking.move_line_ids.filtered(
                lambda ml: ml.state not in ("done", "cancel")
            )
            matched_mls = all_mls.filtered(
                lambda ml: ml.lot_id and ml.lot_id.name in matched_lot_names
            )
            remaining_mls = all_mls - matched_mls

            if not remaining_mls:
                picking.container_id = self.id
            else:
                self._split_picking(picking, matched_mls, remaining_mls)
                picking.container_id = self.id

        # Update container metrics
        self.weight = sum(processed_lines.mapped("assortment_gross_weight"))
        self.volume = sum(processed_lines.mapped("volume"))
        self.package_qty = len(processed_lines)

    def _split_picking(self, picking, matched_mls, remaining_mls):
        """
        Move remaining_mls to a new backorder picking.
        Splits stock.move records when only some of their lines go to the backorder.
        """
        backorder_vals = picking.copy_data(
            default={
                "move_ids": [],
                "move_line_ids": [],
                "backorder_id": picking.id,
            }
        )[0]
        backorder = self.env["stock.picking"].create(backorder_vals)

        # Group remaining move_lines by their parent move
        remaining_by_move = {}
        for ml in remaining_mls:
            remaining_by_move.setdefault(ml.move_id, self.env["stock.move.line"])
            remaining_by_move[ml.move_id] |= ml

        for move, rem_lines in remaining_by_move.items():
            all_move_mls = move.move_line_ids.filtered(
                lambda ml: ml.state not in ("done", "cancel")
            )
            if len(all_move_mls) == len(rem_lines):
                # All lines of this move go to backorder
                move.write({"picking_id": backorder.id})
                rem_lines.write({"picking_id": backorder.id})
            else:
                # Partial: create new move in backorder for remaining lines
                remaining_qty = sum(rem_lines.mapped("quantity"))
                new_move = move.copy(
                    default={
                        "picking_id": backorder.id,
                        "product_uom_qty": remaining_qty,
                        "move_line_ids": [],
                    }
                )
                rem_lines.write(
                    {"picking_id": backorder.id, "move_id": new_move.id}
                )
                # Reduce original move qty to only what stays
                matched_qty = sum((all_move_mls - rem_lines).mapped("quantity"))
                move.product_uom_qty = matched_qty
```

- [ ] **Step 5: Run all tests so far**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist 2>&1 | tail -40
```
Expected: All tests pass (including Task 2/3/4 tests).

- [ ] **Step 6: Commit**

```bash
git add shoes_packinglist/models/purchase_container.py \
        shoes_packinglist/wizard/packing_list_warning_wizard.py \
        shoes_packinglist/tests/test_packing_list_update.py
git commit -m "feat(shoes_packinglist): lot matching, warning wizard, picking split logic"
```

---

## Task 6: Tests for `_process_packing_list_update`

**Files:**
- Modify: `shoes_packinglist/tests/test_packing_list_update.py`

- [ ] **Step 1: Add tests for complete picking, partial split, and container metrics**

Append to `shoes_packinglist/tests/test_packing_list_update.py`:
```python
class TestProcessUpdate(PackingListCommon):
    """Tests for _process_packing_list_update: splitting and metrics."""

    def _container_with_lines(self, lots_in_packing):
        """Helper: container with packing list lines for the given lot names."""
        container = self.env["purchase.container"].create(
            {"code": f"CONT_{lots_in_packing[0]}", "shipping_agent_id": self.partner.id}
        )
        for lot_name in lots_in_packing:
            self.env["purchase.container.line"].create(
                {
                    "container_id": container.id,
                    "lot": lot_name,
                    "assortment_gross_weight": 2.5,
                    "volume": 0.1,
                }
            )
        return container

    def test_complete_picking_gets_container_id(self):
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2])
        container = self._container_with_lines(["LOT001", "LOT002"])
        container.action_update_from_packing_list()
        self.assertEqual(picking.container_id, container)

    def test_container_metrics_updated(self):
        self._make_incoming_picking([self.lot1, self.lot2])
        container = self._container_with_lines(["LOT001", "LOT002"])
        container.action_update_from_packing_list()
        # 2 lines × 2.5 kg = 5.0 kg
        self.assertAlmostEqual(container.weight, 5.0)
        # 2 lines × 0.1 = 0.2 volume
        self.assertAlmostEqual(container.volume, 0.2)
        # 2 lines
        self.assertEqual(container.package_qty, 2)

    def test_partial_picking_creates_backorder(self):
        # Picking has LOT001 + LOT002 + LOT003; packing list only has LOT001
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2, self.lot3])
        container = self._container_with_lines(["LOT001"])
        container.action_update_from_packing_list()

        # Original picking: container_id assigned
        self.assertEqual(picking.container_id, container)

        # Backorder created with LOT002 and LOT003
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        self.assertTrue(backorder, "Backorder picking should be created")
        backorder_lots = backorder.move_line_ids.mapped("lot_id.name")
        self.assertIn("LOT002", backorder_lots)
        self.assertIn("LOT003", backorder_lots)

    def test_partial_picking_container_picking_has_only_matched_lots(self):
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2, self.lot3])
        container = self._container_with_lines(["LOT001"])
        container.action_update_from_packing_list()

        container_lot_names = picking.move_line_ids.mapped("lot_id.name")
        self.assertIn("LOT001", container_lot_names)
        self.assertNotIn("LOT002", container_lot_names)
        self.assertNotIn("LOT003", container_lot_names)

    def test_metrics_only_include_matched_lines(self):
        """When wizard is bypassed via action_continue, only matched lines count."""
        self._make_incoming_picking([self.lot1])
        container = self.env["purchase.container"].create(
            {"code": "CONT_PARTIAL_M", "shipping_agent_id": self.partner.id}
        )
        # One matched line, one unmatched
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOT001",
                "assortment_gross_weight": 3.0,
                "volume": 0.2,
            }
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOTXXX",
                "assortment_gross_weight": 99.0,
                "volume": 99.0,
            }
        )
        result = container.action_update_from_packing_list()
        # Wizard returned for unmatched LOT
        self.assertEqual(result.get("res_model"), "packing.list.warning.wizard")
        # Simulate user clicking "Continue"
        wizard = self.env["packing.list.warning.wizard"].browse(result["res_id"])
        wizard.action_continue()
        # Only the matched line contributes to metrics
        self.assertAlmostEqual(container.weight, 3.0)
        self.assertAlmostEqual(container.volume, 0.2)
        self.assertEqual(container.package_qty, 1)

    def test_wizard_cancel_does_not_update_pickings(self):
        picking, _ = self._make_incoming_picking([self.lot1])
        container = self.env["purchase.container"].create(
            {"code": "CONT_WIZCANCEL", "shipping_agent_id": self.partner.id}
        )
        self.env["purchase.container.line"].create(
            {"container_id": container.id, "lot": "LOT001"}
        )
        self.env["purchase.container.line"].create(
            {"container_id": container.id, "lot": "LOTXXX"}
        )
        result = container.action_update_from_packing_list()
        wizard = self.env["packing.list.warning.wizard"].browse(result["res_id"])
        wizard.action_cancel()
        # Picking should not have container_id set
        self.assertFalse(picking.container_id)
```

- [ ] **Step 2: Run all tests**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist 2>&1 | tail -40
```
Expected: All tests pass.

- [ ] **Step 3: Commit**

```bash
git add shoes_packinglist/tests/test_packing_list_update.py
git commit -m "test(shoes_packinglist): add integration tests for Update logic"
```

---

## Task 7: Views — Container Line + Wizard

**Files:**
- Modify: `shoes_packinglist/views/purchase_container_line_views.xml`
- Modify: `shoes_packinglist/wizard/packing_list_warning_wizard_views.xml`

- [ ] **Step 1: Write `purchase_container_line_views.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="purchase_container_line_view_list" model="ir.ui.view">
        <field name="name">purchase.container.line.list</field>
        <field name="model">purchase.container.line</field>
        <field name="arch" type="xml">
            <list editable="bottom" import="1">
                <field name="lot"/>
                <field name="name" string="Product Ref."/>
                <field name="color"/>
                <field name="assortment"/>
                <field name="pairs"/>
                <field name="purchase_order"/>
                <field name="shippingmark"/>
                <field name="assortment_gross_weight"/>
                <field name="volume"/>
                <field name="move_id" readonly="1"/>
                <field name="shoes_campaign" optional="hide"/>
                <field name="pair_net_weight" optional="hide"/>
                <field name="pair_gross_weight" optional="hide"/>
                <field name="assortment_net_weight" optional="hide"/>
                <field name="high" optional="hide"/>
                <field name="width" optional="hide"/>
                <field name="length" optional="hide"/>
            </list>
        </field>
    </record>

    <record id="purchase_container_line_view_form" model="ir.ui.view">
        <field name="name">purchase.container.line.form</field>
        <field name="model">purchase.container.line</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <group string="Identification">
                            <field name="lot"/>
                            <field name="name" string="Product Ref."/>
                            <field name="color"/>
                            <field name="shoes_campaign"/>
                            <field name="purchase_order"/>
                            <field name="assortment"/>
                            <field name="shippingmark"/>
                        </group>
                        <group string="Quantities">
                            <field name="pairs"/>
                            <field name="move_id" readonly="1"/>
                        </group>
                    </group>
                    <group>
                        <group string="Weights">
                            <field name="pair_net_weight"/>
                            <field name="pair_gross_weight"/>
                            <field name="assortment_net_weight"/>
                            <field name="assortment_gross_weight"/>
                        </group>
                        <group string="Dimensions">
                            <field name="volume"/>
                            <field name="high"/>
                            <field name="width"/>
                            <field name="length"/>
                        </group>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
</odoo>
```

- [ ] **Step 2: Write `packing_list_warning_wizard_views.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="packing_list_warning_wizard_view_form" model="ir.ui.view">
        <field name="name">packing.list.warning.wizard.form</field>
        <field name="model">packing.list.warning.wizard</field>
        <field name="arch" type="xml">
            <form string="Packing List — Lots Not Found">
                <sheet>
                    <group>
                        <field name="container_id" readonly="1"/>
                    </group>
                    <p>
                        The following packing list lines could not be matched
                        to any pending stock move for this shipping agent.
                        You can continue (these lines will be skipped) or cancel
                        to review the data.
                    </p>
                    <field name="warning_line_ids">
                        <list>
                            <field name="lot"/>
                            <field name="name" string="Product Ref."/>
                            <field name="purchase_order"/>
                        </list>
                    </field>
                </sheet>
                <footer>
                    <button
                        name="action_continue"
                        type="object"
                        string="Continue"
                        class="btn-primary"
                    />
                    <button
                        name="action_cancel"
                        type="object"
                        string="Cancel"
                        class="btn-secondary"
                        special="cancel"
                    />
                </footer>
            </form>
        </field>
    </record>
</odoo>
```

- [ ] **Step 3: Verify module updates cleanly**

```bash
python odoo-bin -d <db> -u shoes_packinglist --stop-after-init 2>&1 | tail -10
```
Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add shoes_packinglist/views/purchase_container_line_views.xml \
        shoes_packinglist/wizard/packing_list_warning_wizard_views.xml
git commit -m "feat(shoes_packinglist): add container line and wizard views"
```

---

## Task 8: Views — `purchase.container` Form Extension

**Files:**
- Modify: `shoes_packinglist/views/purchase_container_views.xml`

- [ ] **Step 1: Write the XPath extension**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <!-- Add "Update" button to container header -->
    <record id="purchase_container_form_inherit_packinglist" model="ir.ui.view">
        <field name="name">purchase.container.form.inherit.packinglist</field>
        <field name="model">purchase.container</field>
        <field name="inherit_id" ref="purchase_container.purchase_container_view_form"/>
        <field name="arch" type="xml">

            <!-- Update button before the Lock button -->
            <xpath expr="//header/button[@name='button_lock']" position="before">
                <button
                    name="action_update_from_packing_list"
                    type="object"
                    string="Update"
                    class="btn-primary"
                    invisible="state == 'locked'"
                />
            </xpath>

            <!-- Packing List section after Purchase Orders group -->
            <xpath expr="//field[@name='purchase_order_ids']/.." position="after">
                <group>
                    <separator string="Packing List" colspan="4"/>
                    <field
                        name="container_line_ids"
                        colspan="4"
                        nolabel="1"
                        context="{'default_container_id': active_id}"
                    >
                        <list editable="bottom" import="1">
                            <field name="lot"/>
                            <field name="name" string="Product Ref."/>
                            <field name="color"/>
                            <field name="assortment"/>
                            <field name="pairs"/>
                            <field name="purchase_order"/>
                            <field name="shippingmark"/>
                            <field name="assortment_gross_weight"/>
                            <field name="volume"/>
                            <field name="move_id" readonly="1"/>
                            <field name="shoes_campaign" optional="hide"/>
                            <field name="pair_net_weight" optional="hide"/>
                            <field name="pair_gross_weight" optional="hide"/>
                            <field name="assortment_net_weight" optional="hide"/>
                            <field name="high" optional="hide"/>
                            <field name="width" optional="hide"/>
                            <field name="length" optional="hide"/>
                        </list>
                    </field>
                </group>
            </xpath>

        </field>
    </record>
</odoo>
```

- [ ] **Step 2: Verify the view extension loads without errors**

```bash
python odoo-bin -d <db> -u shoes_packinglist --stop-after-init 2>&1 | grep -E "ERROR|WARNING|shoes_packinglist"
```
Expected: No `ERROR` lines related to `shoes_packinglist`.

- [ ] **Step 3: Run full test suite one last time**

```bash
python odoo-bin -d <db> --test-enable --stop-after-init \
  -u shoes_packinglist \
  --test-tags shoes_packinglist 2>&1 | tail -20
```
Expected: All tests pass.

- [ ] **Step 4: Commit**

```bash
git add shoes_packinglist/views/purchase_container_views.xml
git commit -m "feat(shoes_packinglist): extend container form with packing list section and Update button"
```

---

## Self-Review Checklist

- [x] **Char cleaning** — Task 2 covers `create`/`write` with `_clean_char_fields`. All 7 char fields listed in `_CHAR_FIELDS`. ✓
- [x] **Spreadsheet import** — `import="1"` on both list views enables the standard Odoo import button. ✓
- [x] **Validation: no agent** — Task 4. ✓
- [x] **Validation: no lines** — Task 4. ✓
- [x] **Validation: no pending pickings** — Task 4. ✓
- [x] **Lot matching resets move_id** — `self.container_line_ids.write({"move_id": False})` at start. ✓
- [x] **Wizard on unmatched lots** — Task 5. ✓
- [x] **Complete picking → container_id** — Task 6 test `test_complete_picking_gets_container_id`. ✓
- [x] **Partial picking → backorder** — Task 6 test `test_partial_picking_creates_backorder`. ✓
- [x] **Container metrics update** — Task 6 test `test_container_metrics_updated`. ✓
- [x] **Wizard continue → only matched lines** — Task 6 test `test_metrics_only_include_matched_lines`. ✓
- [x] **Wizard cancel → no side effects** — Task 6 test `test_wizard_cancel_does_not_update_pickings`. ✓
- [x] **move_id field on container.line** — defined in Task 2, used in filtering in Task 5. ✓
- [x] **Security ACLs** — Task 1 covers all 3 models. ✓
- [x] **View: Update button invisible when locked** — `invisible="state == 'locked'"`. ✓
- [x] **View: move_id readonly** — `readonly="1"` in both list views. ✓
- [x] **digits for high/width/length** — `digits="Volume"` as per spec. ✓
