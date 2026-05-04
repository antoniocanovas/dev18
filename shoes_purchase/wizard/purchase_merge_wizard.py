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
