# shoes_purchase — Wizard de división de pedido de compra

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear el módulo `shoes_purchase` con un wizard que divide un pedido de compra en borrador en dos, conservando en el original las líneas seleccionadas y moviendo el resto a un nuevo PO, garantizando la integridad de los lotes.

**Architecture:** Wizard `purchase.split.wizard` (TransientModel) abierto desde un botón en el formulario del PO (solo en estado `draft`). Filtros opcionales en la cabecera del wizard reducen las líneas visibles mediante un campo computed `available_line_ids`. La división mueve líneas vía `write({'order_id': nuevo_po.id})` y regenera lotes directos en ambos POs. Los lotes de SO se mantienen automáticamente por el vínculo `sale_line_id`.

**Tech Stack:** Odoo 18 Enterprise, Python 3, XML views, `purchase`, `sale_purchase`, `shoes_dealer`, `purchase_lot_preassignment`, `shoes_shippingmark`.

---

## Mapa de archivos

| Archivo | Acción | Responsabilidad |
|---|---|---|
| `shoes_purchase/__manifest__.py` | Crear | Declaración del módulo |
| `shoes_purchase/__init__.py` | Crear | Imports de paquete |
| `shoes_purchase/models/__init__.py` | Crear | Import de modelos |
| `shoes_purchase/models/purchase_order.py` | Crear | Método `action_open_split_wizard` en `purchase.order` |
| `shoes_purchase/wizard/__init__.py` | Crear | Import del wizard |
| `shoes_purchase/wizard/purchase_split_wizard.py` | Crear | TransientModel `purchase.split.wizard` con campos, compute y `action_split` |
| `shoes_purchase/views/purchase_split_wizard_views.xml` | Crear | Formulario del wizard |
| `shoes_purchase/views/purchase_order_views.xml` | Crear | Botón en formulario de PO |
| `shoes_purchase/security/ir.model.access.csv` | Crear | ACL del wizard |

---

## Task 1: Estructura base del módulo

**Files:**
- Crear: `shoes_purchase/__manifest__.py`
- Crear: `shoes_purchase/__init__.py`
- Crear: `shoes_purchase/models/__init__.py`
- Crear: `shoes_purchase/wizard/__init__.py`

- [ ] **Crear `shoes_purchase/__manifest__.py`**

```python
{
    "name": "Shoes Purchase",
    "version": "18.0.1.0.0",
    "category": "Purchase",
    "summary": "Wizard para dividir pedidos de compra en dos",
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
        "wizard/purchase_split_wizard_views.xml",
        "views/purchase_order_views.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
```

- [ ] **Crear `shoes_purchase/__init__.py`**

```python
from . import models
from . import wizard
```

- [ ] **Crear `shoes_purchase/models/__init__.py`**

```python
from . import purchase_order
```

- [ ] **Crear `shoes_purchase/wizard/__init__.py`**

```python
from . import purchase_split_wizard
```

- [ ] **Commit**

```bash
git add shoes_purchase/
git commit -m "feat(shoes_purchase): scaffold module structure"
```

---

## Task 2: Seguridad

**Files:**
- Crear: `shoes_purchase/security/ir.model.access.csv`

- [ ] **Crear `shoes_purchase/security/ir.model.access.csv`**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_purchase_split_wizard_user,purchase.split.wizard.user,model_purchase_split_wizard,purchase.group_purchase_user,1,1,1,1
access_purchase_split_wizard_manager,purchase.split.wizard.manager,model_purchase_split_wizard,purchase.group_purchase_manager,1,1,1,1
```

- [ ] **Commit**

```bash
git add shoes_purchase/security/ir.model.access.csv
git commit -m "feat(shoes_purchase): add ACL for purchase.split.wizard"
```

---

## Task 3: Modelo del wizard (`purchase.split.wizard`)

**Files:**
- Crear: `shoes_purchase/wizard/purchase_split_wizard.py`

- [ ] **Crear `shoes_purchase/wizard/purchase_split_wizard.py`**

```python
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseSplitWizard(models.TransientModel):
    _name = "purchase.split.wizard"
    _description = "Wizard para dividir un pedido de compra en dos"

    purchase_order_id = fields.Many2one(
        "purchase.order",
        string="Pedido de compra",
        required=True,
        readonly=True,
    )

    # --- Filtros opcionales ---
    filter_campaign_id = fields.Many2one(
        "project.project",
        string="Temporada",
    )
    filter_partner_id = fields.Many2one(
        "res.partner",
        string="Cliente (SO)",
    )
    filter_product_id = fields.Many2one(
        "product.product",
        string="Artículo",
    )
    filter_product_tmpl_id = fields.Many2one(
        "product.template",
        string="Plantilla de producto",
    )
    filter_shippingmark_id = fields.Many2one(
        "sale.order.type",
        string="Shipping Mark",
    )

    # --- Líneas disponibles según filtros (dominio para line_ids) ---
    # Sin tabla de relación: campo computed no-store no necesita tabla DB
    available_line_ids = fields.Many2many(
        "purchase.order.line",
        string="Líneas disponibles",
        compute="_compute_available_line_ids",
        store=False,
    )

    # --- Líneas a conservar en el PO original ---
    line_ids = fields.Many2many(
        "purchase.order.line",
        "purchase_split_wizard_keep_rel",
        "wizard_id",
        "line_id",
        string="Líneas a conservar en el pedido original",
    )

    @api.depends(
        "purchase_order_id",
        "filter_campaign_id",
        "filter_partner_id",
        "filter_product_id",
        "filter_product_tmpl_id",
        "filter_shippingmark_id",
    )
    def _compute_available_line_ids(self):
        for wiz in self:
            if not wiz.purchase_order_id:
                wiz.available_line_ids = False
                continue
            domain = [("order_id", "=", wiz.purchase_order_id.id)]
            if wiz.filter_campaign_id:
                # shoes_campaign_id no es stored en POL, se filtra por el PO padre
                domain.append(("order_id.shoes_campaign_id", "=", wiz.filter_campaign_id.id))
            if wiz.filter_partner_id:
                # sale_order_id es related stored (sale_line_id.order_id) desde sale_purchase
                domain.append(("sale_order_id.partner_id", "=", wiz.filter_partner_id.id))
            if wiz.filter_product_id:
                domain.append(("product_id", "=", wiz.filter_product_id.id))
            if wiz.filter_product_tmpl_id:
                # product_tmpl_id no es stored en POL, se filtra vía product_id
                domain.append(("product_id.product_tmpl_id", "=", wiz.filter_product_tmpl_id.id))
            if wiz.filter_shippingmark_id:
                domain.append(("pnt_sale_type_id", "=", wiz.filter_shippingmark_id.id))
            wiz.available_line_ids = self.env["purchase.order.line"].search(domain)

    @api.onchange(
        "filter_campaign_id",
        "filter_partner_id",
        "filter_product_id",
        "filter_product_tmpl_id",
        "filter_shippingmark_id",
    )
    def _onchange_filters(self):
        self.line_ids = False

    def action_split(self):
        self.ensure_one()
        po = self.purchase_order_id

        if po.state != "draft":
            raise UserError(_("Solo se pueden dividir pedidos en estado borrador."))
        if not self.line_ids:
            raise UserError(
                _("Selecciona al menos una línea para conservar en el pedido original.")
            )
        if set(self.line_ids.ids) == set(po.order_line.ids):
            raise UserError(_("Debes dejar al menos una línea en el nuevo pedido."))

        lines_to_move = po.order_line - self.line_ids

        new_po = self.env["purchase.order"].create(
            {
                "partner_id": po.partner_id.id,
                "shoes_campaign_id": po.shoes_campaign_id.id or False,
                "currency_id": po.currency_id.id,
                "company_id": po.company_id.id,
                "date_planned": po.date_planned,
                "partner_ref": po.partner_ref,
                "notes": po.notes,
            }
        )

        lines_to_move.write({"order_id": new_po.id})

        po.create_lots_for_purchase_order()
        new_po.create_lots_for_purchase_order()

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Pedido dividido correctamente"),
                "message": _(
                    "Se ha creado el pedido de compra %s con las líneas no seleccionadas.",
                    new_po.name,
                ),
                "type": "success",
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
```

- [ ] **Commit**

```bash
git add shoes_purchase/wizard/purchase_split_wizard.py
git commit -m "feat(shoes_purchase): add purchase.split.wizard model with action_split logic"
```

---

## Task 4: Acción de apertura del wizard en `purchase.order`

**Files:**
- Crear: `shoes_purchase/models/purchase_order.py`

- [ ] **Crear `shoes_purchase/models/purchase_order.py`**

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
```

- [ ] **Commit**

```bash
git add shoes_purchase/models/purchase_order.py
git commit -m "feat(shoes_purchase): add action_open_split_wizard on purchase.order"
```

---

## Task 5: Vista del wizard

**Files:**
- Crear: `shoes_purchase/views/purchase_split_wizard_views.xml`

- [ ] **Crear `shoes_purchase/views/purchase_split_wizard_views.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="purchase_split_wizard_form" model="ir.ui.view">
        <field name="name">purchase.split.wizard.form</field>
        <field name="model">purchase.split.wizard</field>
        <field name="arch" type="xml">
            <form string="Dividir pedido de compra">
                <sheet>
                    <group>
                        <field name="purchase_order_id" readonly="1"/>
                        <field name="available_line_ids" invisible="1"/>
                    </group>
                    <group string="Filtros">
                        <group>
                            <field name="filter_campaign_id"/>
                            <field name="filter_product_id"/>
                            <field name="filter_product_tmpl_id"/>
                        </group>
                        <group>
                            <field name="filter_partner_id"/>
                            <field name="filter_shippingmark_id"/>
                        </group>
                    </group>
                    <separator string="Líneas a conservar en el pedido original"/>
                    <field name="line_ids"
                           nolabel="1"
                           domain="[('id', 'in', available_line_ids)]">
                        <list string="Líneas a conservar">
                            <field name="product_id"/>
                            <field name="sale_order_id" string="Pedido de venta" optional="show"/>
                            <field name="pnt_sale_type_id" string="Shipping Mark" optional="show"/>
                            <field name="product_qty" string="Cantidad"/>
                            <field name="price_unit" string="Precio unit."/>
                            <field name="pairs_count" string="Pares" optional="show"/>
                        </list>
                    </field>
                    <div class="alert alert-info mt-2" role="alert">
                        Las líneas <strong>no seleccionadas</strong> del pedido original
                        pasarán al nuevo pedido de compra.
                    </div>
                </sheet>
                <footer>
                    <button string="Dividir pedido"
                            name="action_split"
                            type="object"
                            class="btn-primary"/>
                    <button string="Cancelar" class="btn-secondary" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>
</odoo>
```

- [ ] **Commit**

```bash
git add shoes_purchase/views/purchase_split_wizard_views.xml
git commit -m "feat(shoes_purchase): add wizard form view"
```

---

## Task 6: Botón en el formulario de `purchase.order`

**Files:**
- Crear: `shoes_purchase/views/purchase_order_views.xml`

El botón se inserta después del botón existente de etiquetas de lotes (`action_view_associated_lots`) definido por `purchase_lot_preassignment`.

- [ ] **Crear `shoes_purchase/views/purchase_order_views.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="shoes_purchase_order_form_inherit" model="ir.ui.view">
        <field name="name">shoes.purchase.order.form.inherit</field>
        <field name="model">purchase.order</field>
        <field name="inherit_id" ref="purchase.purchase_order_form"/>
        <field name="arch" type="xml">
            <xpath expr="//div[@name='button_box']" position="inside">
                <button name="action_open_split_wizard"
                        string="Dividir pedido"
                        type="object"
                        class="oe_stat_button"
                        icon="fa-scissors"
                        invisible="state != 'draft'"/>
            </xpath>
        </field>
    </record>
</odoo>
```

- [ ] **Commit**

```bash
git add shoes_purchase/views/purchase_order_views.xml
git commit -m "feat(shoes_purchase): add split button on purchase.order form"
```

---

## Task 7: Verificación manual

Pasos de verificación que debe ejecutar el usuario en la interfaz:

- [ ] Instalar el módulo `shoes_purchase` desde Ajustes → Módulos
- [ ] Abrir un pedido de compra en estado **Borrador** con al menos 2 líneas
- [ ] Verificar que aparece el botón **"Dividir pedido"** en los stat-buttons
- [ ] Abrir el wizard: confirmar que se muestran los filtros y la tree vacía
- [ ] Aplicar un filtro (p.ej. Shipping Mark) → verificar que `line_ids` se vacía
- [ ] Seleccionar líneas mediante "Añadir una línea" → se añaden a la tree
- [ ] Pulsar **"Dividir pedido"** → debe aparecer notificación con el nombre del nuevo PO
- [ ] Verificar que el PO original solo contiene las líneas seleccionadas
- [ ] Abrir el nuevo PO → verificar que contiene el resto de líneas, mismo proveedor y campaña
- [ ] Si hay líneas directas (sin SO) con productos `is_assortment`: verificar que los lotes del PO original tienen `ref = PO_original.name` y los del nuevo tienen `ref = nuevo_PO.name`
- [ ] Intentar dividir un PO confirmado → debe mostrar UserError
- [ ] Intentar dividir sin seleccionar líneas → debe mostrar UserError
- [ ] Intentar seleccionar TODAS las líneas → debe mostrar UserError

---

## Notas de implementación

**Por qué `lines_to_move.write({'order_id': new_po.id})` no rompe validaciones:**
- `shoes_shippingmark` lanza `UserError` solo cuando se cambia `product_qty` en líneas con `sale_line_id`. Aquí solo se cambia `order_id`. ✓
- `purchase_lot_preassignment` solo dispara `create_lots_for_purchase_order()` en `write` cuando hay cambio de `product_qty`. El `action_split` lo llama explícitamente. ✓

**Por qué los lotes de SO no necesitan acción:**
- `stock.lot.ref = SO.name`. El lote apunta al SO, no al PO.
- `purchase.order._get_sale_orders()` = `order_line.sale_order_id` (= `sale_line_id.order_id`).
- Al mover la POL al nuevo PO, `nuevo_po._get_sale_orders()` ya encuentra ese SO y sus lotes. ✓

**`shoes_campaign_id` en las líneas movidas:**
- Es un campo `related="order_id.shoes_campaign_id"` (store=True) en `purchase.order.line` (de `shoes_dealer`).
- Tras el `write({'order_id': new_po.id})`, Odoo recomputa el campo y lo actualiza al `shoes_campaign_id` del nuevo PO, que es el mismo que el original. ✓
