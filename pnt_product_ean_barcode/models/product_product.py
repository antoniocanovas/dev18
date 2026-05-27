# Copyright Puntsistemes.es


from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    pnt_ean_required = fields.Boolean(
        string="EAN required", related="categ_id.pnt_ean_required"
    )
    barcode = fields.Char(copy=True, tracking=True)

    def action_open_assign_ean_wizard(self) -> dict:
        """Open wizard to assign EAN with default sequence from category"""
        self.ensure_one()
        return {
            "name": "Assign EAN",
            "type": "ir.actions.act_window",
            "res_model": "pnt.assign.ean.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "active_model": "product.product",
                "active_ids": self.ids,
                "active_id": self.id,
            },
        }
