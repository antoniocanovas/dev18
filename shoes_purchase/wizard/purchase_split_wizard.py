from odoo import _, fields, models
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

    line_ids = fields.Many2many(
        "purchase.order.line",
        "purchase_split_wizard_keep_rel",
        "wizard_id",
        "line_id",
        string="Líneas a conservar en el pedido original",
    )

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
