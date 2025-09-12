from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    only_preassigned_lots = fields.Boolean(
        string="Preassigned Lots",
        default=True,
        help=(
            "If checked, only preassigned lots/serial numbers will be allowed during "
            "reception"
        ),
    )

    @api.model_create_multi
    def create(self, vals_list: list[dict]) -> models.Model:
        """Set default value for only_preassigned_lots on incoming pickings"""
        # Ensure vals_list is a list
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        # Pre-process vals_list to set defaults
        for vals in vals_list:
            # Set default for incoming pickings linked to purchase orders
            if (
                vals.get("picking_type_code") == "incoming"
                and vals.get("purchase_id")
                and "only_preassigned_lots" not in vals
            ):
                vals["only_preassigned_lots"] = True
        return super().create(vals_list)

    def _validate_expected_lots(self) -> None:
        """Validate that received lots match expected ones"""
        if self.picking_type_code != "incoming" or not self.purchase_id:
            return
        for move in self.move_ids:
            if move.product_id.tracking in ["lot", "serial"]:
                self._validate_move_lots(move)

    def _validate_move_lots(self, move: models.Model) -> None:
        """Validate lots for a specific move - only for received quantities"""
        # Only validate products that are actually being received (qty_done > 0)
        received_lines = move.move_line_ids.filtered(lambda ml: ml.qty_done > 0)
        
        if not received_lines:
            return  # No quantities received, skip validation
            
        # Get expected lots for this product from purchase order
        # Include 'received' state to handle lots that might have been marked as received
        expected_lots = self.env["purchase.lot.preassignment"].search(
            [
                ("purchase_order_id", "=", self.purchase_id.id),
                ("product_id", "=", move.product_id.id),
                ("state", "in", ["draft", "confirmed", "received"]),
            ]
        )
        
        # Get received lots only from lines with qty_done > 0
        received_lots = []
        received_qty = 0
        for line in received_lines:
            received_qty += line.qty_done
            if line.lot_id:
                received_lots.append(line.lot_id.name)
            elif line.lot_name:
                received_lots.append(line.lot_name)
                
        if not received_lots:
            return  # No lots received, nothing to validate
            
        # For serial tracking, validate that received qty matches number of serials
        if move.product_id.tracking == "serial":
            if len(received_lots) != received_qty:
                raise ValidationError(
                    _(
                        "Product %s with serial tracking requires one serial number "
                        "per unit received. Received quantity: %s, Serial numbers provided: %s"
                    )
                    % (move.product_id.display_name, int(received_qty), len(received_lots))
                )
        
        # If only_preassigned_lots is True, enforce strict validation
        if self.only_preassigned_lots:
            if not expected_lots:
                # No preassigned lots but trying to receive with lots
                raise ValidationError(
                    _(
                        "Product %s has no preassigned lots, but lot/serial numbers "
                        'were provided. Either disable "Preassigned Lots" or create '
                        "preassigned lots first."
                    )
                    % move.product_id.display_name
                )
            expected_names = expected_lots.mapped("name")
            invalid_lots = set(received_lots) - set(expected_names)
            
            # Check for duplicate receptions (lots already marked as received)
            already_received = expected_lots.filtered(
                lambda l: l.name in received_lots and l.state == 'received'
            )
            
            # For partial deliveries, allow "resetting" lots that were prematurely marked as received
            # if they're not actually in a completed stock move
            if already_received:
                # Check if these lots are really in completed stock moves
                really_received = []
                for lot_rec in already_received:
                    # Search for completed stock moves with this lot
                    completed_moves = self.env['stock.move.line'].search([
                        ('lot_id.name', '=', lot_rec.name),
                        ('product_id', '=', move.product_id.id),
                        ('state', '=', 'done'),
                        ('picking_id.purchase_id', '=', self.purchase_id.id)
                    ])
                    if completed_moves:
                        really_received.append(lot_rec.name)
                    else:
                        # Reset lot state if it's not really in a completed move
                        lot_rec.write({'state': 'confirmed'})
                        
                if really_received:
                    raise ValidationError(
                        _(
                            "The following lot/serial numbers for product %s were already "
                            "received and processed in completed deliveries: %s\n\n"
                            "Available lots for reception: %s\n\n"
                            "Please use different lot/serial numbers."
                        )
                        % (
                            move.product_id.display_name,
                            ", ".join(really_received),
                            ", ".join(expected_lots.filtered(lambda l: l.state != 'received').mapped('name')) or "None available",
                        )
                    )
            
            if invalid_lots:
                # Get available (non-received) lots for better error message
                available_lots = expected_lots.filtered(lambda l: l.state in ['draft', 'confirmed'])
                raise ValidationError(
                    _(
                        "The following lot/serial numbers are not in the preassigned "
                        "list for product %s: %s\n\nExpected lots: %s\n\n"
                        "Available lots (not yet received): %s\n\nTo receive "
                        'these lots, either:\n- Disable "Preassigned Lots" option\n- '
                        "Add these lots to the preassigned list in the purchase order"
                    )
                    % (
                        move.product_id.display_name,
                        ", ".join(invalid_lots),
                        ", ".join(expected_names) if expected_names else "None",
                        ", ".join(available_lots.mapped('name')) if available_lots else "All lots already received",
                    )
                )
        # If only_preassigned_lots is False, just log warnings (existing behavior)
        else:
            if not expected_lots:
                return  # No expected lots, skip validation
            expected_names = expected_lots.mapped("name")
            # Only warn about missing lots that were supposed to be received
            received_expected = set(received_lots) & set(expected_names) 
            missing_from_received = set(received_lots) - set(expected_names)
            
            warnings = []
            if missing_from_received:
                warnings.append(
                    _("Unexpected lots received: %s") % ", ".join(missing_from_received)
                )
            
            if warnings:
                message = _("Lot validation warnings for product %s:\n%s") % (
                    move.product_id.display_name,
                    "\n".join(warnings),
                )
                # Log warning in chatter
                self.message_post(
                    body=message,
                    message_type="notification",
                    subtype_xmlid="mail.mt_note",
                )

    def button_validate(self) -> object:
        """Override to validate lots before confirmation"""
        # Validate expected lots
        self._validate_expected_lots()
        # Continue with standard validation
        result = super().button_validate()
        # Mark preassigned lots as received
        self._mark_lots_as_received()
        return result

    def _mark_lots_as_received(self) -> None:
        """Mark preassigned lots as received"""
        if self.picking_type_code != "incoming" or not self.purchase_id:
            return
        for move in self.move_ids:
            if move.product_id.tracking in ["lot", "serial"]:
                self._mark_move_lots_received(move)

    def _mark_move_lots_received(self, move: models.Model) -> None:
        """Mark lots as received for a specific move - only for received quantities"""
        # Only process lines with qty_done > 0
        received_lines = move.move_line_ids.filtered(lambda ml: ml.qty_done > 0)
        
        received_lot_names = []
        for line in received_lines:
            if line.lot_id:
                received_lot_names.append(line.lot_id.name)
            elif line.lot_name:
                received_lot_names.append(line.lot_name)
                
        if received_lot_names:
            preassigned_lots = self.env["purchase.lot.preassignment"].search(
                [
                    ("purchase_order_id", "=", self.purchase_id.id),
                    ("product_id", "=", move.product_id.id),
                    ("name", "in", received_lot_names),
                    ("state", "in", ["draft", "confirmed"]),
                ]
            )
            preassigned_lots.action_mark_received()

    def action_view_expected_lots(self) -> dict:
        """View expected lots for this picking"""
        self.ensure_one()
        if not self.purchase_id:
            raise UserError(_("This picking is not linked to a purchase order"))
        return {
            "name": _("Expected Lots"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.lot.preassignment",
            "view_mode": "list,form",
            "domain": [("purchase_order_id", "=", self.purchase_id.id)],
        }


class StockMove(models.Model):
    _inherit = "stock.move"

    expected_lot_names = fields.Char(
        string="Expected Lots",
        compute="_compute_expected_lot_names",
        help="Expected lot/serial numbers for this move",
    )

    @api.depends("purchase_line_id", "product_id")
    def _compute_expected_lot_names(self):
        for move in self:
            if move.purchase_line_id and move.product_id.tracking in ["lot", "serial"]:
                expected_lots = self.env["purchase.lot.preassignment"].search(
                    [
                        ("purchase_line_id", "=", move.purchase_line_id.id),
                        ("product_id", "=", move.product_id.id),
                        ("state", "in", ["draft", "confirmed"]),
                    ]
                )
                names = expected_lots.mapped("name")
                move.expected_lot_names = ", ".join(names) if names else ""
            else:
                move.expected_lot_names = ""


class StockMoveLine(models.Model):
    _inherit = "stock.move.line"

    is_expected_lot = fields.Boolean(
        string="Is Expected Lot",
        compute="_compute_is_expected_lot",
        help="True if this lot was expected in preassignments",
    )

    @api.depends("lot_id", "lot_name", "move_id.purchase_line_id")
    def _compute_is_expected_lot(self):
        for line in self:
            line.is_expected_lot = False

            if not line.move_id.purchase_line_id:
                continue

            lot_name = line.lot_id.name if line.lot_id else line.lot_name
            if not lot_name:
                continue

            expected_lot = self.env["purchase.lot.preassignment"].search(
                [
                    ("purchase_line_id", "=", line.move_id.purchase_line_id.id),
                    ("name", "=", lot_name),
                    ("state", "in", ["draft", "confirmed"]),
                ],
                limit=1,
            )

            line.is_expected_lot = bool(expected_lot)
