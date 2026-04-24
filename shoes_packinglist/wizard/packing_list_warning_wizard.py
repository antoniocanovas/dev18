from odoo import api, fields, models


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
    pending_picking_ids = fields.Many2many(
        "stock.picking",
        compute="_compute_pending_picking_ids",
        string="Pending Receipts",
    )

    @api.depends("container_id")
    def _compute_pending_picking_ids(self):
        for wizard in self:
            if not wizard.container_id.shipping_agent_id:
                wizard.pending_picking_ids = False
                continue
            wizard.pending_picking_ids = self.env["stock.picking"].search(
                [
                    ("partner_id", "=", wizard.container_id.shipping_agent_id.id),
                    ("picking_type_id.code", "=", "incoming"),
                    (
                        "state",
                        "in",
                        ["assigned", "waiting", "confirmed", "partially_available"],
                    ),
                    ("container_id", "=", False),
                ]
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
