from odoo import api, fields, models, _
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    lot_preassignment_ids = fields.One2many(
        'purchase.lot.preassignment',
        'purchase_order_id',
        string='Lot Preassignments'
    )
    lot_preassignment_count = fields.Integer(
        string='Preassigned Lots Count',
        compute='_compute_lot_preassignment_count'
    )
    has_lot_tracking_lines = fields.Boolean(
        string='Has Lot Tracking Lines',
        compute='_compute_has_lot_tracking_lines',
        help='True if any order line has lot/serial tracking'
    )

    @api.depends('lot_preassignment_ids')
    def _compute_lot_preassignment_count(self):
        for order in self:
            order.lot_preassignment_count = len(order.lot_preassignment_ids)

    @api.depends('order_line.product_id.tracking')
    def _compute_has_lot_tracking_lines(self):
        for order in self:
            order.has_lot_tracking_lines = any(
                line.product_id.tracking in ['lot', 'serial'] 
                for line in order.order_line
            )

    def action_generate_lot_preassignments(self):
        """Generate lot preassignments for all lines with tracking"""
        self.ensure_one()
        
        if not self.has_lot_tracking_lines:
            raise UserError(_('No lines with lot/serial tracking found'))
        
        # Remove existing preassignments in draft state
        self.lot_preassignment_ids.filtered(lambda x: x.state == 'draft').unlink()
        
        preassignments = []
        for line in self.order_line:
            if line.product_id.tracking in ['lot', 'serial']:
                preassignments.extend(self._generate_line_preassignments(line))
        
        if preassignments:
            self.env['purchase.lot.preassignment'].create(preassignments)
            
        return self.action_view_lot_preassignments()

    def _generate_line_preassignments(self, line):
        """Generate preassignments for a specific line"""
        preassignments = []
        
        if line.product_id.tracking == 'serial':
            # For serial numbers, create one preassignment per unit
            qty_to_assign = int(line.product_qty)
            for i in range(qty_to_assign):
                preassignments.append({
                    'purchase_order_id': self.id,
                    'purchase_line_id': line.id,
                    'name': self._generate_lot_name(line, i + 1),
                    'product_qty': 1.0,
                    'sequence': i + 1,
                })
        else:
            # For lots, create preassignments based on lot size or default
            lot_size = self._get_lot_size(line)
            remaining_qty = line.product_qty
            sequence = 1
            
            while remaining_qty > 0:
                qty = min(lot_size, remaining_qty)
                preassignments.append({
                    'purchase_order_id': self.id,
                    'purchase_line_id': line.id,
                    'name': self._generate_lot_name(line, sequence),
                    'product_qty': qty,
                    'sequence': sequence,
                })
                remaining_qty -= qty
                sequence += 1
        
        return preassignments

    def _generate_lot_name(self, line, sequence):
        """Generate lot/serial name"""
        product_code = line.product_id.default_code or line.product_id.name[:10]
        order_name = self.name.replace('/', '')
        
        if line.product_id.tracking == 'serial':
            return f"{product_code}-{order_name}{sequence:04d}"
        else:
            return f"{product_code}-{order_name}{sequence:03d}"

    def _get_lot_size(self, line):
        """Get lot size for the line (can be customized)"""
        # Default lot size, can be extended to use product configuration
        return 100.0

    def action_view_lot_preassignments(self):
        """Open lot preassignments view"""
        self.ensure_one()
        
        action = {
            'name': _('Lot Preassignments'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.lot.preassignment',
            'view_mode': 'list,form',
            'context': {
                'default_purchase_order_id': self.id,
                'search_default_purchase_order_id': self.id,
            },
            'domain': [('purchase_order_id', '=', self.id)],
        }
        
        if self.lot_preassignment_count == 1:
            action.update({
                'view_mode': 'form',
                'res_id': self.lot_preassignment_ids.id,
            })
        
        return action

    def button_confirm(self):
        """Override to confirm lot preassignments"""
        res = super().button_confirm()
        
        # Confirm all draft preassignments
        self.lot_preassignment_ids.filtered(
            lambda x: x.state == 'draft'
        ).action_confirm()
        
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    lot_preassignment_ids = fields.One2many(
        'purchase.lot.preassignment',
        'purchase_line_id',
        string='Lot Preassignments'
    )
    lot_preassignment_count = fields.Integer(
        string='Preassigned Lots Count',
        compute='_compute_lot_preassignment_count'
    )
    expected_lot_names = fields.Char(
        string='Expected Lots',
        compute='_compute_expected_lot_names',
        help='List of expected lot/serial numbers'
    )

    @api.depends('lot_preassignment_ids')
    def _compute_lot_preassignment_count(self):
        for line in self:
            line.lot_preassignment_count = len(line.lot_preassignment_ids)

    @api.depends('lot_preassignment_ids.name')
    def _compute_expected_lot_names(self):
        for line in self:
            names = line.lot_preassignment_ids.mapped('name')
            line.expected_lot_names = ', '.join(names) if names else ''

    def action_view_lot_preassignments(self):
        """Open lot preassignments view for this line"""
        self.ensure_one()
        
        return {
            'name': _('Line Lot Preassignments'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.lot.preassignment',
            'view_mode': 'list,form',
            'context': {
                'default_purchase_order_id': self.order_id.id,
                'default_purchase_line_id': self.id,
            },
            'domain': [('purchase_line_id', '=', self.id)],
        }
