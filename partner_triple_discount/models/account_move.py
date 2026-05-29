from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    discount1 = fields.Float(string="Discount 1 (%)", digits="Discount")
    discount2 = fields.Float(string="Discount 2 (%)", digits="Discount")
    discount3 = fields.Float(string="Discount 3 (%)", digits="Discount")

    @api.onchange("partner_id")
    def _onchange_partner_id_triple_discount(self):
        if self.partner_id:
            self.discount1 = self.partner_id.discount1
            self.discount2 = self.partner_id.discount2
            self.discount3 = self.partner_id.discount3

    def action_open_triple_discount_wizard(self):
        self.ensure_one()
        return {
            "name": _("Apply Discounts"),
            "type": "ir.actions.act_window",
            "res_model": "account.move.triple.discount",
            "view_mode": "form",
            "target": "new",
            "context": {"default_move_id": self.id},
        }
