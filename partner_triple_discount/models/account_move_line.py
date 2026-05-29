from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        move_id = self.env.context.get("default_move_id")
        if not move_id:
            return defaults
        move = self.env["account.move"].browse(move_id)
        for field in ("discount1", "discount2", "discount3"):
            if field in fields_list:
                defaults.setdefault(field, move[field])
        return defaults
