from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    container_ids = fields.Many2many(
        "purchase.container",
        "purchase_container_account_move_rel",
        "move_id",
        "container_id",
        string="Containers",
        copy=False,
    )
