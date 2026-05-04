# shoes_purchase — Wizard de fusión de pedidos de compra

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Añadir al módulo `shoes_purchase` una acción contextual en la lista de pedidos de compra que abre un wizard de confirmación para fusionar N pedidos en borrador del mismo proveedor y campaña en el más reciente, manteniendo la integridad de lotes.

**Architecture:** `ir.actions.server` enlazada a la lista de `purchase.order` abre `purchase.merge.wizard`. El wizard valida los POs seleccionados, muestra un resumen y al confirmar mueve todas las líneas al PO superviviente (id más alto), actualiza su cabecera, elimina los absorbidos y regenera lotes directos.

**Tech Stack:** Odoo 18 Enterprise, Python 3, XML views/data, `purchase`, `sale_purchase`, `shoes_dealer`, `purchase_lot_preassignment`, `shoes_shippingmark`.

---

## Mapa de archivos

| Archivo | Acción | Responsabilidad |
|---|---|---|
| `shoes_purchase/__manifest__.py` | Modificar | Añadir 3 nuevos archivos en `data` |
| `shoes_purchase/wizard/__init__.py` | Modificar | Añadir import `purchase_merge_wizard` |
| `shoes_purchase/models/purchase_order.py` | Modificar | Añadir método `action_open_merge_wizard` |
| `shoes_purchase/wizard/purchase_merge_wizard.py` | Crear | TransientModel con validación, compute y `action_merge` |
| `shoes_purchase/wizard/purchase_merge_wizard_views.xml` | Crear | Formulario del wizard de confirmación |
| `shoes_purchase/data/purchase_merge_server_action.xml` | Crear | Server action enlazada a lista de PO |

---

## Task 1: Modelo `purchase.merge.wizard`

**Files:**
- Crear: `shoes_purchase/wizard/purchase_merge_wizard.py`

- [ ] **Crear `shoes_purchase/wizard/purchase_merge_wizard.py`**

```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseMergeWizard(models.TransientModel):
    _name = "purchase.merge.wizard"
    _description = "Wizard para fusionar pedidos de compra"

    purchase_order_ids = fields.Many2many(
        "purchase.order",
        "purchase_merge_wizard_po_rel",
        "wizard_id",
        "order_id",
        string="Pedidos a fusionar",
        readonly=True,
    )

    survivor_id = fields.Many2one(
        "purchase.order",
        string="Pedido superviviente",
        compute="_compute_survivor_id",
        store=False,
    )

    merged_notes = fields.Text(
        string="Notas fusionadas",
        compute="_compute_merged_notes",
        store=False,
    )

    can_merge = fields.Boolean(
        string="Se puede fusionar",
        compute="_compute_validation",
        store=False,
    )

    validation_error = fields.Char(
        string="Error de validación",
        compute="_compute_validation",
        store=False,
    )

    @api.depends("purchase_order_ids")
    def _compute_survivor_id(self):
        for wiz in self:
            if wiz.purchase_order_ids:
                wiz.survivor_id = wiz.purchase_order_ids.sorted("id", reverse=True)[0]
            else:
                wiz.survivor_id = False

    @api.depends("purchase_order_ids")
    def _compute_merged_notes(self):
        for wiz in self:
            notes = [po.notes for po in wiz.purchase_order_ids if po.notes]
            wiz.merged_notes = "\n".join(notes) if notes else False

    @api.depends("purchase_order_ids")
    def _compute_validation(self):
        for wiz in self:
            pos = wiz.purchase_order_ids
            if len(pos) < 2:
                wiz.validation_error = _("Selecciona al menos 2 pedidos de compra.")
                wiz.can_merge = False
                continue
            if len(pos.mapped("partner_id")) > 1:
                wiz.validation_error = _("Todos los pedidos deben ser del mismo proveedor.")
                wiz.can_merge = False
                continue
            if any(po.state != "draft" for po in pos):
                wiz.validation_error = _("Solo se pueden fusionar pedidos en estado borrador.")
                wiz.can_merge = False
                continue
            campaign_values = set(po.shoes_campaign_id.id or False for po in pos)
            if len(campaign_values) > 1:
                wiz.validation_error = _("Todos los pedidos deben tener la misma campaña.")
                wiz.can_merge = False
                continue
            wiz.validation_error = False
            wiz.can_merge = True

    def action_merge(self):
        self.ensure_one()
        pos = self.purchase_order_ids

        if len(pos) < 2:
            raise UserError(_("Selecciona al menos 2 pedidos de compra."))
        if len(pos.mapped("partner_id")) > 1:
            raise UserError(_("Todos los pedidos deben ser del mismo proveedor."))
        if any(po.state != "draft" for po in pos):
            raise UserError(_("Solo se pueden fusionar pedidos en estado borrador."))
        campaign_values = set(po.shoes_campaign_id.id or False for po in pos)
        if len(campaign_values) > 1:
            raise UserError(_("Todos los pedidos deben tener la misma campaña."))

        survivor = self.survivor_id
        to_absorb = pos - survivor

        to_absorb.order_line.write({"order_id": survivor.id})

        valid_dates = [po.date_planned for po in pos if po.date_planned]
        if valid_dates:
            survivor.date_planned = max(valid_dates)

        if self.merged_notes:
            survivor.notes = self.merged_notes

        for po in to_absorb:
            po._delete_unused_po_lots()
        to_absorb.unlink()

        survivor.create_lots_for_purchase_order()

        return {
            "type": "ir.actions.act_window",
            "res_model": "purchase.order",
            "res_id": survivor.id,
            "view_mode": "form",
            "target": "current",
        }
```

- [ ] **Commit**

```bash
git add shoes_purchase/wizard/purchase_merge_wizard.py
git commit -m "feat(shoes_purchase): add purchase.merge.wizard model with action_merge logic"
```

---

## Task 2: Vista del wizard de fusión

**Files:**
- Crear: `shoes_purchase/wizard/purchase_merge_wizard_views.xml`

- [ ] **Crear `shoes_purchase/wizard/purchase_merge_wizard_views.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="purchase_merge_wizard_form" model="ir.ui.view">
        <field name="name">purchase.merge.wizard.form</field>
        <field name="model">purchase.merge.wizard</field>
        <field name="arch" type="xml">
            <form string="Fusionar pedidos de compra">
                <sheet>
                    <field name="can_merge" invisible="1"/>
                    <field name="survivor_id" invisible="1"/>
                    <div class="alert alert-danger" role="alert" invisible="can_merge">
                        <field name="validation_error" readonly="1" nolabel="1"/>
                    </div>
                    <group invisible="not can_merge">
                        <group string="Pedido superviviente">
                            <field name="survivor_id" readonly="1"/>
                        </group>
                        <group string="Notas fusionadas">
                            <field name="merged_notes" readonly="1" nolabel="1"/>
                        </group>
                    </group>
                    <separator string="Pedidos que se fusionarán" invisible="not can_merge"/>
                    <field name="purchase_order_ids"
                           readonly="1"
                           nolabel="1"
                           invisible="not can_merge">
                        <list string="Pedidos a fusionar">
                            <field name="name"/>
                            <field name="partner_id"/>
                            <field name="shoes_campaign_id"/>
                            <field name="date_planned" string="Fecha entrega"/>
                            <field name="amount_total" string="Total"/>
                        </list>
                    </field>
                    <div class="alert alert-warning mt-2" role="alert" invisible="not can_merge">
                        Los pedidos <strong>no supervivientes</strong> serán
                        <strong>eliminados</strong> tras la fusión. Esta operación
                        no se puede deshacer.
                    </div>
                </sheet>
                <footer>
                    <button string="Fusionar"
                            name="action_merge"
                            type="object"
                            class="btn-primary"
                            invisible="not can_merge"/>
                    <button string="Cancelar" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>
</odoo>
```

- [ ] **Commit**

```bash
git add shoes_purchase/wizard/purchase_merge_wizard_views.xml
git commit -m "feat(shoes_purchase): add merge wizard form view"
```

---

## Task 3: Server action contextual en lista de POs

**Files:**
- Crear: `shoes_purchase/data/purchase_merge_server_action.xml`

- [ ] **Crear directorio `shoes_purchase/data/`** (si no existe)

```bash
mkdir -p shoes_purchase/data
```

- [ ] **Crear `shoes_purchase/data/purchase_merge_server_action.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="action_purchase_merge" model="ir.actions.server">
        <field name="name">Fusionar pedidos</field>
        <field name="model_id" ref="purchase.model_purchase_order"/>
        <field name="binding_model_id" ref="purchase.model_purchase_order"/>
        <field name="binding_view_types">list</field>
        <field name="state">code</field>
        <field name="code">action = records.action_open_merge_wizard()</field>
    </record>
</odoo>
```

- [ ] **Commit**

```bash
git add shoes_purchase/data/purchase_merge_server_action.xml
git commit -m "feat(shoes_purchase): add server action to open merge wizard from PO list"
```

---

## Task 4: Actualizar archivos existentes

**Files:**
- Modificar: `shoes_purchase/__manifest__.py`
- Modificar: `shoes_purchase/wizard/__init__.py`
- Modificar: `shoes_purchase/models/purchase_order.py`

- [ ] **Actualizar `shoes_purchase/__manifest__.py`**

Añadir los 3 nuevos archivos en la clave `data`, respetando el orden (security → data → wizard → views):

```python
{
    "name": "Shoes Purchase",
    "version": "18.0.1.0.0",
    "category": "Purchase",
    "summary": "Wizard para dividir y fusionar pedidos de compra",
    "author": "Punt Sistemes",
    "depends": [
        "purchase",
        "sale_purchase",
        "shoes_dealer",
        "purchase_lot_preassignment",
        "shoes_shippingmark",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/purchase_merge_server_action.xml",
        "wizard/purchase_split_wizard_views.xml",
        "wizard/purchase_merge_wizard_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
```

- [ ] **Actualizar `shoes_purchase/wizard/__init__.py`**

```python
from . import purchase_split_wizard
from . import purchase_merge_wizard
```

- [ ] **Actualizar `shoes_purchase/models/purchase_order.py`**

Añadir el método `action_open_merge_wizard` a la clase existente:

```python
from odoo import models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_open_split_wizard(self):
        self.ensure_one()
        return {
            "name": "Dividir pedido de compra",
            "type": "ir.actions.act_window",
            "res_model": "purchase.split.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_purchase_order_id": self.id},
        }

    def action_open_merge_wizard(self):
        return {
            "name": "Fusionar pedidos de compra",
            "type": "ir.actions.act_window",
            "res_model": "purchase.merge.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_purchase_order_ids": self.ids},
        }
```

- [ ] **Commit**

```bash
git add shoes_purchase/__manifest__.py shoes_purchase/wizard/__init__.py shoes_purchase/models/purchase_order.py
git commit -m "feat(shoes_purchase): wire merge wizard into module (manifest, init, purchase_order)"
```

---

## Task 5: Verificación manual

Pasos que debe ejecutar el usuario en la interfaz:

- [ ] Actualizar módulo `shoes_purchase` desde Ajustes → Módulos (upgrade)
- [ ] Ir a Compras → Pedidos de compra en vista **lista**
- [ ] Verificar que existe la acción **"Fusionar pedidos"** en el menú de acciones (⚙)
- [ ] Seleccionar 1 PO → ejecutar acción → verificar mensaje "Selecciona al menos 2 pedidos"
- [ ] Seleccionar 2 POs de distinto proveedor → verificar mensaje "mismo proveedor"
- [ ] Seleccionar 2 POs de mismo proveedor pero distinta campaña → verificar mensaje "misma campaña"
- [ ] Seleccionar 2 POs draft del mismo proveedor y campaña → verificar wizard con resumen correcto (superviviente = PO con id más alto, notas fusionadas, fechas)
- [ ] Confirmar fusión → verificar que se abre el PO superviviente con todas las líneas
- [ ] Verificar que los POs absorbidos ya no existen
- [ ] Si había líneas directas `is_assortment` sin SO: verificar lotes con `ref = PO_superviviente.name`
- [ ] Verificar que los lotes de SO siguen accesibles desde el PO superviviente

---

## Notas de implementación

**Orden en `data` del manifest:** La server action se carga antes que las vistas del wizard porque Odoo carga los datos en orden y la server action solo referencia el modelo, no la vista. Si se invirtiera el orden, no habría problema funcional, pero por convención `data/` va antes que `wizard/views/`.

**`action_open_merge_wizard` sin `ensure_one`:** A diferencia del split wizard (que opera sobre un único PO), el merge recibe un recordset de N registros desde `records` en la server action. Por eso no se llama `ensure_one()`.

**Eliminación de POs absorbidos:** `to_absorb.unlink()` funciona en draft porque Odoo no permite hacer unlink de POs confirmados. La validación previa `state == 'draft'` lo garantiza.

**`_delete_unused_po_lots` antes de `unlink`:** Limpia los lotes con `ref = PO_absorbido.name` que no tengan movimientos (ninguno en draft). Sin esta llamada, quedarían lotes huérfanos con referencias a POs eliminados.
