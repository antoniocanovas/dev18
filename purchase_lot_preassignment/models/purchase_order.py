from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    lot_preassignment_ids = fields.One2many(
        "purchase.lot.preassignment", "purchase_order_id", string="Lot Preassignments"
    )
    lot_preassignment_count = fields.Integer(
        string="Preassigned Lots Count", compute="_compute_lot_preassignment_count"
    )
    has_lot_tracking_lines = fields.Boolean(
        string="Has Lot Tracking Lines",
        compute="_compute_has_lot_tracking_lines",
        help="True if any order line has lot/serial tracking",
    )

    @api.depends("lot_preassignment_ids")
    def _compute_lot_preassignment_count(self):
        for order in self:
            order.lot_preassignment_count = len(order.lot_preassignment_ids)

    @api.depends("order_line.product_id.tracking")
    def _compute_has_lot_tracking_lines(self):
        for order in self:
            order.has_lot_tracking_lines = any(
                line.product_id.tracking in ["lot", "serial"]
                for line in order.order_line
            )

    def action_generate_lot_preassignments(self) -> dict:
        """Generate lot preassignments for all lines with tracking"""
        self.ensure_one()

        if not self.has_lot_tracking_lines:
            raise UserError(_("No lines with lot/serial tracking found"))

        # Only remove existing preassignments in draft state that exceed current quantities
        # This allows incremental generation when quantities are increased
        preassignments = []
        for line in self.order_line:
            if line.product_id.tracking in ["lot", "serial"]:
                preassignments.extend(self._generate_line_preassignments(line))

        if preassignments:
            self.env["purchase.lot.preassignment"].create(preassignments)

        return self.action_view_lot_preassignments()

    def _generate_line_preassignments(self, line: models.Model) -> list[dict]:
        """Generate preassignments for a specific line - only create missing ones"""
        preassignments = []
        
        # Count existing preassignments for this line (all states)
        existing_preassignments = line.lot_preassignment_ids
        existing_count = len(existing_preassignments)
        required_count = int(line.product_qty)
        
        # If we have more than needed, remove excess draft ones
        if existing_count > required_count:
            excess_count = existing_count - required_count
            excess_preassignments = existing_preassignments.filtered(
                lambda p: p.state == 'draft'
            ).sorted('sequence', reverse=True)[:excess_count]
            if excess_preassignments:
                excess_preassignments.unlink()
            return []  # No new preassignments needed
        
        # If we have exactly what we need, return empty
        if existing_count >= required_count:
            return []
            
        # Calculate how many new preassignments we need
        missing_count = required_count - existing_count
        
        # Get the next sequence number
        next_sequence = (max(existing_preassignments.mapped('sequence')) if existing_preassignments else 0) + 1

        if line.product_id.tracking == "serial":
            # For serial numbers, create one preassignment per missing unit
            for i in range(missing_count):
                preassignments.append(
                    {
                        "purchase_order_id": self.id,
                        "purchase_line_id": line.id,
                        "name": self._generate_lot_name(line, next_sequence + i),
                        "product_qty": 1.0,
                        "sequence": next_sequence + i,
                    }
                )
        else:
            # For lots, create preassignments based on lot size or default
            lot_size = self._get_lot_size(line)
            remaining_qty = missing_count * 1.0  # Convert to float for lot handling
            sequence = next_sequence

            while remaining_qty > 0:
                qty = min(lot_size, remaining_qty)
                preassignments.append(
                    {
                        "purchase_order_id": self.id,
                        "purchase_line_id": line.id,
                        "name": self._generate_lot_name(line, sequence),
                        "product_qty": qty,
                        "sequence": sequence,
                    }
                )
                remaining_qty -= qty
                sequence += 1

        return preassignments

    def _generate_lot_name(self, line: models.Model, sequence: int) -> str:
        """Generate lot/serial name using standard Odoo sequence"""
        # Use standard Odoo sequence for Serial Numbers
        return self.env['ir.sequence'].next_by_code('stock.lot.serial') or 'SN-ERROR'

    def _get_lot_size(self, line: models.Model) -> float:
        """Get lot size for the line (can be customized)"""
        # Default lot size, can be extended to use product configuration
        return 100.0

    def action_view_lot_preassignments(self) -> dict:
        """Open lot preassignments view"""
        self.ensure_one()

        action = {
            "name": _("Lot Preassignments"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.lot.preassignment",
            "view_mode": "list,form",
            "context": {
                "default_purchase_order_id": self.id,
                "search_default_purchase_order_id": self.id,
            },
            "domain": [("purchase_order_id", "=", self.id)],
        }

        if self.lot_preassignment_count == 1:
            action.update(
                {
                    "view_mode": "form",
                    "res_id": self.lot_preassignment_ids.id,
                }
            )

        return action

    def button_confirm(self) -> object:
        """Override to confirm lot preassignments"""
        res = super().button_confirm()

        # Confirm all draft preassignments
        self.lot_preassignment_ids.filtered(
            lambda x: x.state == "draft"
        ).action_confirm()

        return res


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    lot_preassignment_ids = fields.One2many(
        "purchase.lot.preassignment", "purchase_line_id", string="Lot Preassignments"
    )
    lot_preassignment_count = fields.Integer(
        string="Preassigned Lots Count", compute="_compute_lot_preassignment_count"
    )
    expected_lot_names = fields.Char(
        string="Expected Lots",
        compute="_compute_expected_lot_names",
        help="List of expected lot/serial numbers",
    )

    @api.depends("lot_preassignment_ids")
    def _compute_lot_preassignment_count(self):
        for line in self:
            line.lot_preassignment_count = len(line.lot_preassignment_ids)

    @api.depends("lot_preassignment_ids.name")
    def _compute_expected_lot_names(self):
        for line in self:
            names = line.lot_preassignment_ids.mapped("name")
            line.expected_lot_names = ", ".join(names) if names else ""

    def action_view_lot_preassignments(self) -> dict:
        """Open lot preassignments view for this line"""
        self.ensure_one()

        return {
            "name": _("Line Lot Preassignments"),
            "type": "ir.actions.act_window",
            "res_model": "purchase.lot.preassignment",
            "view_mode": "list,form",
            "context": {
                "default_purchase_order_id": self.order_id.id,
                "default_purchase_line_id": self.id,
            },
            "domain": [("purchase_line_id", "=", self.id)],
        }
