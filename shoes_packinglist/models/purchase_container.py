from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class PurchaseContainer(models.Model):
    _inherit = "purchase.container"

    container_line_ids = fields.One2many(
        "purchase.container.line",
        "container_id",
        string="Packing List",
        copy=False,
    )
    container_line_count = fields.Integer(
        compute="_compute_container_line_count",
        string="Packing List Lines",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Purchase Currency",
        compute="_compute_currency_id",
        store=True,
        readonly=False,
        copy=False,
    )
    duty_currency_id = fields.Many2one(
        "res.currency",
        string="Duty Currency",
        copy=False,
    )
    currency_exchange = fields.Float(
        string="Currency Exchange",
        digits=(16, 6),
    )

    @api.depends("container_line_ids")
    def _compute_container_line_count(self):
        for rec in self:
            rec.container_line_count = len(rec.container_line_ids)

    @api.depends("code", "shipping_agent_id.ref", "shipping_agent_id.name", "duty_currency_id.name")
    def _compute_name(self):
        for rec in self:
            parts = []
            agent = rec.shipping_agent_id
            if agent:
                parts.append(agent.ref or agent.name or "")
            if rec.duty_currency_id:
                parts.append(rec.duty_currency_id.name)
            rec.name = "{} ({})".format(rec.code, ", ".join(parts)) if parts else (rec.code or "")

    @api.depends("shipping_agent_id")
    def _compute_currency_id(self):
        for rec in self:
            rec.currency_id = rec.shipping_agent_id.property_purchase_currency_id or False

    def action_open_validate_wizard(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Validar albaranes"),
            "res_model": "container.validate.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {"default_container_id": self.id},
        }

    def action_print_packing_list(self):
        self.ensure_one()
        result = self.action_update_from_packing_list()
        # If unmatched lots exist, a wizard is returned — show it instead of printing
        if isinstance(result, dict):
            return result
        return self.env.ref("shoes_packinglist.action_report_packing_list").report_action(self)

    def _get_packing_list_report_data(self):
        """Returns grouped lines and grand totals for the packing list QWeb template."""
        self.ensure_one()
        groups_dict = {}
        group_order = []
        for line in self.container_line_ids:
            heading = line.tariff_heading or ""
            if heading not in groups_dict:
                groups_dict[heading] = {
                    "tariff_heading": heading,
                    "lines": [],
                    "total_quantity": 0.0,
                    "total_net_weight": 0.0,
                    "total_gross_weight": 0.0,
                    "total_pairs": 0.0,
                }
                group_order.append(heading)
            g = groups_dict[heading]
            g["lines"].append(line)
            g["total_quantity"] += line.quantity
            g["total_net_weight"] += line.assortment_net_weight
            g["total_gross_weight"] += line.assortment_gross_weight
            g["total_pairs"] += line.pair_qty

        groups = [groups_dict[h] for h in group_order]
        grand_total = {
            "quantity": sum(g["total_quantity"] for g in groups),
            "net_weight": sum(g["total_net_weight"] for g in groups),
            "gross_weight": sum(g["total_gross_weight"] for g in groups),
            "pairs": sum(g["total_pairs"] for g in groups),
        }
        return {"groups": groups, "grand_total": grand_total}

    def action_view_packing_list(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("Packing List"),
            "res_model": "purchase.container.line",
            "view_mode": "list,form",
            "domain": [("container_id", "=", self.id)],
            "context": {"default_container_id": self.id},
        }

    def action_update_from_packing_list(self):
        self.ensure_one()

        # --- Validation ---
        if not self.shipping_agent_id:
            raise UserError(
                _(
                    "Debe definir el agente de transporte (Shipping Agent) "
                    "del contenedor."
                )
            )
        if not self.container_line_ids:
            raise UserError(
                _(
                    "No hay líneas en el packing list. "
                    "Importe las líneas antes de actualizar."
                )
            )
        pending_pickings = self.env["stock.picking"].search(
            [
                ("partner_id", "=", self.shipping_agent_id.id),
                ("picking_type_id.code", "=", "incoming"),
                (
                    "state",
                    "in",
                    ["assigned", "waiting", "confirmed", "partially_available"],
                ),
            ]
        )
        if not pending_pickings:
            raise UserError(
                _('El proveedor "%s" no tiene albaranes de recepción pendientes.')
                % self.shipping_agent_id.name
            )

        # --- Lot matching ---
        # Lots from purchase_lot_preassignment exist as stock.lot records but are not
        # yet assigned to incoming move lines before reception. Match each lot to the
        # stock.move in the pending picking via the lot's product, with a more precise
        # secondary filter through the sale order when lot.ref is available.
        #
        # After a picking split, multiple moves exist for the same product. We use two
        # strategies to pick the correct one:
        #   1. If a move line already has this lot pre-assigned, use that move directly.
        #   2. Among candidates, choose the first with remaining capacity (fewer
        #      lot-assigned move lines than product_qty), also counting claims made
        #      earlier in this same matching loop to handle multi-line containers.
        self.container_line_ids.write({"move_id": False})

        unmatched = self.env["purchase.container.line"]
        session_lot_counts = {}  # move.id → lots claimed in this matching loop
        for line in self.container_line_ids:
            if not line.lot:
                unmatched |= line
                continue
            lot = self.env["stock.lot"].search(
                [
                    ("name", "=", line.lot),
                    ("company_id", "=", self.env.company.id),
                ],
                limit=1,
            )
            if not lot:
                unmatched |= line
                continue

            # Priority 1: move that already has this lot on a pre-assigned move line
            move = False
            existing_ml = self.env["stock.move.line"].search(
                [
                    ("lot_id", "=", lot.id),
                    ("picking_id", "in", pending_pickings.ids),
                    ("state", "not in", ["done", "cancel"]),
                ],
                limit=1,
            )
            if existing_ml:
                move = existing_ml.move_id
            else:
                # Build base domain: product in pending pickings, not done/cancel
                base_domain = [
                    ("picking_id", "in", pending_pickings.ids),
                    ("product_id", "=", lot.product_id.id),
                    ("state", "not in", ["done", "cancel"]),
                ]
                # Prefer match through the sale order chain (lot.ref = SO name)
                candidates = self.env["stock.move"]
                if lot.ref:
                    candidates = self.env["stock.move"].search(
                        base_domain
                        + [
                            (
                                "purchase_line_id.sale_line_id.order_id.name",
                                "=",
                                lot.ref,
                            )
                        ]
                    )
                if not candidates:
                    candidates = self.env["stock.move"].search(base_domain)

                # Pick the first candidate that still has capacity for another lot
                rounding = lot.product_id.uom_id.rounding
                for candidate in candidates:
                    existing_lot_lines = len(
                        candidate.move_line_ids.filtered(
                            lambda ml: ml.lot_id
                            and ml.state not in ("done", "cancel")
                        )
                    )
                    session_claims = session_lot_counts.get(candidate.id, 0)
                    if float_compare(
                        float(existing_lot_lines + session_claims),
                        candidate.product_qty,
                        precision_rounding=rounding,
                    ) < 0:
                        move = candidate
                        break

            if move:
                line.move_id = move
                session_lot_counts[move.id] = session_lot_counts.get(move.id, 0) + 1
            else:
                unmatched |= line

        # --- Open wizard if there are unmatched lines ---
        if unmatched:
            wizard = self.env["packing.list.warning.wizard"].create(
                {
                    "container_id": self.id,
                    "warning_line_ids": [
                        (
                            0,
                            0,
                            {
                                "lot": ln.lot,
                                "name": ln.name,
                                "purchase_order": ln.purchase_order,
                            },
                        )
                        for ln in unmatched
                    ],
                }
            )
            return {
                "type": "ir.actions.act_window",
                "res_model": "packing.list.warning.wizard",
                "res_id": wizard.id,
                "view_mode": "form",
                "target": "new",
            }

        # --- All matched: proceed directly ---
        self._process_packing_list_update()
        return True

    def _process_packing_list_update(self):
        """Split pickings and update container metrics. Called after lot matching."""
        self.ensure_one()

        # Clear container reference from any lot previously linked to this container
        self.env["stock.lot"].search([("container_id", "=", self.id)]).write(
            {"container_line_id": False}
        )

        processed_lines = self.container_line_ids.filtered("move_id")
        if not processed_lines:
            return

        involved_pickings = processed_lines.mapped("move_id.picking_id")

        for picking in involved_pickings:
            picking_lines = processed_lines.filtered(
                lambda l: l.move_id.picking_id == picking
            )
            matched_moves = picking_lines.mapped("move_id")
            all_moves = picking.move_ids.filtered(
                lambda m: m.state not in ("done", "cancel")
            )
            remaining_moves = all_moves - matched_moves

            # Split partially-covered moves: when fewer container lines than move qty
            for move in matched_moves:
                lines_for_move = picking_lines.filtered(lambda l: l.move_id == move)
                container_qty = float(len(lines_for_move))
                rounding = move.product_id.uom_id.rounding
                if float_compare(container_qty, move.product_qty, precision_rounding=rounding) < 0:
                    backorder_qty = move.product_qty - container_qty
                    new_move_vals_list = move._split(backorder_qty)
                    if new_move_vals_list:
                        new_move = self.env["stock.move"].create(new_move_vals_list)
                        remaining_moves |= new_move
                        # Redistribute pre-assigned lot move lines: lots not in this
                        # container belong to the backorder move
                        container_lot_names = set(lines_for_move.mapped("lot"))
                        backorder_mls = move.move_line_ids.filtered(
                            lambda ml: ml.lot_id
                            and ml.lot_id.name not in container_lot_names
                            and ml.state not in ("done", "cancel")
                        )
                        if backorder_mls:
                            backorder_mls.write({
                                "move_id": new_move.id,
                                "picking_id": new_move.picking_id.id,
                            })

            if not remaining_moves:
                picking.container_id = self.id
            else:
                self._split_picking(picking, remaining_moves)
                picking.container_id = self.id

        # Assign lots to move lines so the picking can be validated
        self._assign_lots_to_moves(processed_lines)

        # Update container metrics
        self.weight = sum(processed_lines.mapped("assortment_gross_weight"))
        self.volume = sum(processed_lines.mapped("volume"))
        self.package_qty = len(processed_lines)

        # Update product weight/volume data from packing list
        self._update_product_weights_from_packing_list(processed_lines)

    def _assign_lots_to_moves(self, processed_lines):
        """
        Pre-assign lots to stock.move.line records so the picking can be validated.

        purchase_lot_preassignment creates stock.lot records but does not put them
        on move lines before reception. This method creates one move line per
        packing list line with the matched lot and its quantity (pairs).

        Existing no-lot move lines (created by action_assign) are removed first
        to avoid duplicates.
        """
        # Remove generic no-lot move lines from all matched moves
        matched_moves = processed_lines.mapped("move_id")
        for move in matched_moves:
            move.move_line_ids.filtered(
                lambda ml: not ml.lot_id and ml.state not in ("done", "cancel")
            ).unlink()

        # Create one move line per packing list line with the specific lot
        for line in processed_lines:
            lot = self.env["stock.lot"].search(
                [("name", "=", line.lot), ("company_id", "=", self.env.company.id)],
                limit=1,
            )
            if not lot:
                continue
            move = line.move_id
            # Skip if this lot is already on a move line (idempotent re-run)
            if move.move_line_ids.filtered(
                lambda ml: ml.lot_id == lot and ml.state not in ("done", "cancel")
            ):
                continue
            self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": move.picking_id.id,
                    "product_id": lot.product_id.id,
                    "lot_id": lot.id,
                    "quantity": 1.0,
                    "product_uom_id": move.product_uom.id,
                    "location_id": move.location_id.id,
                    "location_dest_id": move.location_dest_id.id,
                }
            )

    def _update_product_weights_from_packing_list(self, processed_lines):
        """
        Update weight, net_weight, volume and dimensions (product_length,
        product_height, product_width, dimensional_uom_id) on product.product
        and stock.lot. Field names match those from the product_dimension module.

        For assortment products: writes to product.product directly (the related
        fields on product.template mirror these values automatically).
        For pair products (linked via product_tmpl_single_id): writes
        pair_gross_weight, pair_net_weight, volume / pairs to product.template only.

        Lot writes are per-line (each lot is unique). Product writes are deduplicated
        by product.id — the last line in the loop wins for the product.
        """
        cm_uom = self.env.ref("uom.product_uom_cm", raise_if_not_found=False)
        seen_product_ids = set()
        for line in processed_lines:
            if not line.move_id:
                continue
            product = line.move_id.product_id
            if not product:
                continue

            # Update lot fields (per line, no deduplication)
            lot = self.env["stock.lot"].search(
                [("name", "=", line.lot), ("company_id", "=", self.env.company.id)],
                limit=1,
            )
            if lot:
                lot_vals = {
                    "weight": line.assortment_gross_weight,
                    "net_weight": line.assortment_net_weight,
                    "volume": line.volume,
                    "container_line_id": line.id,
                    "product_length": line.length,
                    "product_height": line.high,
                    "product_width": line.width,
                }
                if cm_uom:
                    lot_vals["dimensional_uom_id"] = cm_uom.id
                lot.write(lot_vals)

            # Deduplicate product/template writes by product.id
            if product.id in seen_product_ids:
                continue
            seen_product_ids.add(product.id)

            # Update assortment product (weight/net_weight/dimensions).
            # volume is a stored computed field in product_dimension — it is
            # automatically recomputed from the dimension fields we write here,
            # so there is no need to set it explicitly.
            assortment_vals = {
                "weight": line.assortment_gross_weight,
                "net_weight": line.assortment_net_weight,
                "product_length": line.length,
                "product_height": line.high,
                "product_width": line.width,
            }
            if cm_uom:
                assortment_vals["dimensional_uom_id"] = cm_uom.id
            product.write(assortment_vals)

            # Update pair products (template only, no dimensions)
            pair_tmpl = getattr(product, "product_tmpl_single_id", False)
            if not pair_tmpl:
                continue
            pair_qty = line.pair_qty or 1.0
            pair_vals = {
                "weight": line.pair_gross_weight,
                "net_weight": line.pair_net_weight,
                "volume": line.volume / pair_qty,
            }
            pair_tmpl.write(pair_vals)

    def _split_picking(self, picking, remaining_moves):
        """
        Move remaining_moves to a new backorder picking.
        Lots are not yet on move lines at packing list import time, so the split
        operates at the stock.move level (whole moves), not at the move line level.
        """
        backorder_vals = picking.copy_data(
            default={
                "move_ids": [],
                "move_line_ids": [],
                "backorder_id": picking.id,
            }
        )[0]
        backorder = self.env["stock.picking"].create(backorder_vals)

        for move in remaining_moves:
            pending_mls = move.move_line_ids.filtered(
                lambda ml: ml.state not in ("done", "cancel")
            )
            move.write({"picking_id": backorder.id})
            if pending_mls:
                pending_mls.write({"picking_id": backorder.id})

        backorder.with_context(do_not_check_immediately_transfer=True).action_confirm()
