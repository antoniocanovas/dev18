from odoo import api, fields, models


class AccountMoveTripleDiscount(models.TransientModel):
    _name = "account.move.triple.discount"
    _description = "Invoice Triple Discount Wizard"

    move_id = fields.Many2one(
        comodel_name="account.move",
        required=True,
        default=lambda self: self.env.context.get("default_move_id"),
    )
    discount1 = fields.Float(string="Discount 1 (%)", digits="Discount")
    discount2 = fields.Float(string="Discount 2 (%)", digits="Discount")
    discount3 = fields.Float(string="Discount 3 (%)", digits="Discount")

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        move_id = defaults.get("move_id") or self.env.context.get("default_move_id")
        if move_id:
            move = self.env["account.move"].browse(move_id)
            for field in ("discount1", "discount2", "discount3"):
                if field in fields_list:
                    defaults[field] = move[field]
        return defaults

    def action_apply_discount(self):
        self.ensure_one()
        self.move_id.invoice_line_ids.write(
            {
                "discount1": self.discount1,
                "discount2": self.discount2,
                "discount3": self.discount3,
            }
        )
