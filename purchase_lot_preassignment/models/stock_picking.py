from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    only_preassigned_lots = fields.Boolean(
        string='Preassigned Lots',
        default=True,
        help='If checked, only preassigned lots/serial numbers will be allowed during reception'
    )

    @api.model_create_multi
    def create(self, vals_list):
        """Set default value for only_preassigned_lots on incoming pickings"""
        # Ensure vals_list is a list
        if not isinstance(vals_list, list):
            vals_list = [vals_list]
        
        # Pre-process vals_list to set defaults
        for vals in vals_list:
            # Set default for incoming pickings linked to purchase orders
            if (vals.get('picking_type_code') == 'incoming' and 
                vals.get('purchase_id') and 
                'only_preassigned_lots' not in vals):
                vals['only_preassigned_lots'] = True
        
        return super().create(vals_list)

    def _validate_expected_lots(self):
        """Validate that received lots match expected ones"""
        if self.picking_type_code != 'incoming' or not self.purchase_id:
            return
        
        for move in self.move_ids:
            if move.product_id.tracking in ['lot', 'serial']:
                self._validate_move_lots(move)

    def _validate_move_lots(self, move):
        """Validate lots for a specific move"""
        # Get expected lots for this product from purchase order (any valid state)
        expected_lots = self.env['purchase.lot.preassignment'].search([
            ('purchase_order_id', '=', self.purchase_id.id),
            ('product_id', '=', move.product_id.id),
            ('state', 'in', ['draft', 'confirmed'])
        ])
        
        # Get received lots
        received_lots = []
        for line in move.move_line_ids:
            if line.lot_id:
                received_lots.append(line.lot_id.name)
            elif line.lot_name:
                received_lots.append(line.lot_name)
        
        if not received_lots:
            return  # No lots received, nothing to validate
        
        # If only_preassigned_lots is True, enforce strict validation
        if self.only_preassigned_lots:
            if not expected_lots:
                # No preassigned lots but trying to receive with lots
                raise ValidationError(
                    _('Product %s has no preassigned lots, but lot/serial numbers were provided. '
                      'Either disable "Preassigned Lots" or create preassigned lots first.') % 
                    move.product_id.display_name
                )
            
            expected_names = expected_lots.mapped('name')
            invalid_lots = set(received_lots) - set(expected_names)
            
            if invalid_lots:
                raise ValidationError(
                    _('The following lot/serial numbers are not in the preassigned list for product %s: %s\n\n'
                      'Expected lots: %s\n\n'
                      'To receive these lots, either:\n'
                      '- Disable "Preassigned Lots" option\n'
                      '- Add these lots to the preassigned list in the purchase order') % (
                        move.product_id.display_name,
                        ', '.join(invalid_lots),
                        ', '.join(expected_names) if expected_names else 'None'
                    )
                )
        
        # If only_preassigned_lots is False, just log warnings (existing behavior)
        else:
            if not expected_lots:
                return  # No expected lots, skip validation
            
            expected_names = expected_lots.mapped('name')
            missing_lots = set(expected_names) - set(received_lots)
            extra_lots = set(received_lots) - set(expected_names)
            
            warnings = []
            if missing_lots:
                warnings.append(_('Missing expected lots: %s') % ', '.join(missing_lots))
            if extra_lots:
                warnings.append(_('Unexpected lots received: %s') % ', '.join(extra_lots))
            
            if warnings:
                message = _('Lot validation warnings for product %s:\n%s') % (
                    move.product_id.display_name,
                    '\n'.join(warnings)
                )
                
                # Log warning in chatter
                self.message_post(
                    body=message,
                    message_type='notification',
                    subtype_xmlid='mail.mt_note'
                )

    def button_validate(self):
        """Override to validate lots before confirmation"""
        # Validate expected lots
        self._validate_expected_lots()
        
        # Continue with standard validation
        result = super().button_validate()
        
        # Mark preassigned lots as received
        self._mark_lots_as_received()
        
        return result

    def _mark_lots_as_received(self):
        """Mark preassigned lots as received"""
        if self.picking_type_code != 'incoming' or not self.purchase_id:
            return
        
        for move in self.move_ids:
            if move.product_id.tracking in ['lot', 'serial']:
                self._mark_move_lots_received(move)

    def _mark_move_lots_received(self, move):
        """Mark lots as received for a specific move"""
        received_lot_names = []
        for line in move.move_line_ids:
            if line.lot_id:
                received_lot_names.append(line.lot_id.name)
            elif line.lot_name:
                received_lot_names.append(line.lot_name)
        
        if received_lot_names:
            preassigned_lots = self.env['purchase.lot.preassignment'].search([
                ('purchase_order_id', '=', self.purchase_id.id),
                ('product_id', '=', move.product_id.id),
                ('name', 'in', received_lot_names),
                ('state', 'in', ['draft', 'confirmed'])
            ])
            
            preassigned_lots.action_mark_received()

    def action_view_expected_lots(self):
        """View expected lots for this picking"""
        self.ensure_one()
        
        if not self.purchase_id:
            raise UserError(_('This picking is not linked to a purchase order'))
        
        return {
            'name': _('Expected Lots'),
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.lot.preassignment',
            'view_mode': 'list,form',
            'domain': [('purchase_order_id', '=', self.purchase_id.id)],
        }


class StockMove(models.Model):
    _inherit = 'stock.move'

    expected_lot_names = fields.Char(
        string='Expected Lots',
        compute='_compute_expected_lot_names',
        help='Expected lot/serial numbers for this move'
    )

    @api.depends('purchase_line_id', 'product_id')
    def _compute_expected_lot_names(self):
        for move in self:
            if move.purchase_line_id and move.product_id.tracking in ['lot', 'serial']:
                expected_lots = self.env['purchase.lot.preassignment'].search([
                    ('purchase_line_id', '=', move.purchase_line_id.id),
                    ('product_id', '=', move.product_id.id),
                    ('state', 'in', ['draft', 'confirmed'])
                ])
                names = expected_lots.mapped('name')
                move.expected_lot_names = ', '.join(names) if names else ''
            else:
                move.expected_lot_names = ''


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    is_expected_lot = fields.Boolean(
        string='Is Expected Lot',
        compute='_compute_is_expected_lot',
        help='True if this lot was expected in preassignments'
    )

    @api.depends('lot_id', 'lot_name', 'move_id.purchase_line_id')
    def _compute_is_expected_lot(self):
        for line in self:
            line.is_expected_lot = False
            
            if not line.move_id.purchase_line_id:
                continue
            
            lot_name = line.lot_id.name if line.lot_id else line.lot_name
            if not lot_name:
                continue
            
            expected_lot = self.env['purchase.lot.preassignment'].search([
                ('purchase_line_id', '=', line.move_id.purchase_line_id.id),
                ('name', '=', lot_name),
                ('state', 'in', ['draft', 'confirmed'])
            ], limit=1)
            
            line.is_expected_lot = bool(expected_lot)
