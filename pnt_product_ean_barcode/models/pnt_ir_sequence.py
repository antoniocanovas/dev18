# Copyright Puntsistemes SL


import re
from typing import Any

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_digits_re = re.compile(r"^[0-9]+$")
ir_sequence = "ir.sequence"


class IrSequence(models.Model):
    _inherit = ir_sequence

    pnt_is_ean = fields.Boolean(
        string="EAN", help="Check if this sequence is for EAN codes"
    )
    pnt_ean14_prefix = fields.Char(string="EAN-14 prefix", size=1)
    pnt_max_sequence = fields.Integer(
        string="Max Sequence Number",
        help="Maximum sequence number allowed for EAN codes. Leave 0 for unlimited.",
    )
    pnt_remaining_sequences = fields.Integer(
        string="Remaining Sequences",
        compute="_compute_remaining_sequences",
        store=False,
    )

    @api.depends("pnt_max_sequence", "number_next_actual")
    def _compute_remaining_sequences(self):
        for record in self:
            if record.pnt_is_ean and record.pnt_max_sequence > 0:
                record.pnt_remaining_sequences = max(
                    0, record.pnt_max_sequence - record.number_next_actual + 1
                )
            else:
                record.pnt_remaining_sequences = 0

    def action_open_ean_sequence(self) -> dict[str, str | Any]:
        res_id = self.search([("code", "=", "pnt.product.ean.code")], limit=1)
        print(res_id)
        return {
            "name": _("EAN Sequence"),
            "type": "ir.actions.act_window",
            "res_model": ir_sequence,
            "view_mode": "form",
            "view_type": "form",
            "view_id": self.env.ref("pnt_product_ean_barcode.pnt_sequence_view").id,
            "res_id": res_id.id,
            "target": "new",
        }

    def action_open_internal_ean_sequence(self) -> dict[str, str | Any]:
        res_id = self.search([("code", "=", "pnt.product.internal.ean.code")], limit=1)
        print(res_id)
        return {
            "name": _("Internal EAN Sequence"),
            "type": "ir.actions.act_window",
            "res_model": ir_sequence,
            "view_mode": "form",
            "view_type": "form",
            "view_id": self.env.ref("pnt_product_ean_barcode.pnt_sequence_view").id,
            "res_id": res_id.id,
            "target": "new",
        }

    def isdigits(self, number: object) -> bool:
        try:
            return bool(_digits_re.match(number))
        except ValidationError:
            return False

    @api.onchange("prefix", "pnt_ean14_prefix")
    def validate(self):
        if self.pnt_is_ean:
            if self.prefix and not self.isdigits(self.prefix):
                raise ValidationError(_("EAN prefix must be only numbers "))
            if self.pnt_ean14_prefix and not self.isdigits(self.pnt_ean14_prefix):
                raise ValidationError(_("EAN-14 prefix must be only numbers "))

    @api.constrains("pnt_max_sequence", "number_next_actual")
    def _check_max_sequence(self):
        for record in self:
            if record.pnt_is_ean and record.pnt_max_sequence > 0:
                if record.number_next_actual > record.pnt_max_sequence:
                    raise ValidationError(
                        _("Next Number (%s) cannot exceed Max Sequence Number (%s)")
                        % (record.number_next_actual, record.pnt_max_sequence)
                    )
