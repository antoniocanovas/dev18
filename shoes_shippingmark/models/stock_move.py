# Copyright 2024 Punt Sistemes SL

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_assign(self):
        # Fast path: already running inside a SM-filtered context, skip re-processing
        if self.env.context.get("shoes_allowed_shippingmark_ids") is not None:
            return super()._action_assign()

        restricted_groups = {}  # {(sm_id, ...): (sm_ids list, moves recordset)}
        normal_moves = self.browse()

        for move in self:
            picking = move.picking_id
            if not (
                picking
                and picking.picking_type_code == "outgoing"
                and move.product_id.is_assortment
            ):
                normal_moves |= move
                continue

            partner = picking.partner_id.commercial_partner_id
            sm_ids = partner.shoes_shippingmark_ids
            if not sm_ids:
                normal_moves |= move
                continue

            key = tuple(sorted(sm_ids.ids))
            if key not in restricted_groups:
                restricted_groups[key] = (sm_ids.ids, self.browse())
            restricted_groups[key] = (
                restricted_groups[key][0],
                restricted_groups[key][1] | move,
            )

        if not restricted_groups:
            # Nothing to restrict — proceed normally
            return super()._action_assign()

        # Normal moves: use False to signal "no restriction" and skip re-entry
        if normal_moves:
            normal_moves.with_context(
                shoes_allowed_shippingmark_ids=False
            )._action_assign()

        # Restricted moves: each group gets its allowed SM list in context
        for sm_ids, moves in restricted_groups.values():
            moves.with_context(
                shoes_allowed_shippingmark_ids=sm_ids
            )._action_assign()
