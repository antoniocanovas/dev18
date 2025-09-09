from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class PurchaseLotPreassignment(models.Model):
    _name = 'purchase.lot.preassignment'
    _description = 'Purchase Lot Preassignment'
    _order = 'purchase_line_id, sequence, name'

    name = fields.Char(
        string='Lot/Serial Number',
        required=True,
        help='Preassigned lot or serial number'
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
        help='Sequence for ordering'
    )
    purchase_order_id = fields.Many2one(
        'purchase.order',
        string='Purchase Order',
        required=True,
        ondelete='cascade'
    )
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        required=True,
        ondelete='cascade'
    )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        related='purchase_line_id.product_id',
        store=True
    )
    product_qty = fields.Float(
        string='Quantity',
        default=1.0,
        help='Quantity for this lot/serial number'
    )
    tracking = fields.Selection(
        related='product_id.tracking',
        string='Tracking Type',
        store=True
    )
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('received', 'Received'),
            ('canceled', 'Canceled')
        ],
        string='Status',
        default='draft',
        help='Status of the preassigned lot'
    )
    stock_lot_id = fields.Many2one(
        'stock.lot',
        string='Stock Lot',
        help='Related stock lot when created'
    )
    notes = fields.Text(
        string='Notes',
        help='Additional notes for this preassignment'
    )
    
    # Campos de seguimiento
    date_created = fields.Datetime(
        string='Creation Date',
        default=fields.Datetime.now
    )
    date_confirmed = fields.Datetime(
        string='Confirmation Date'
    )
    date_received = fields.Datetime(
        string='Reception Date'
    )

    @api.constrains('name', 'product_id')
    def _check_unique_lot_serial(self):
        """Validate uniqueness for serial numbers"""
        for record in self:
            if record.tracking == 'serial':
                existing = self.search([
                    ('name', '=', record.name),
                    ('product_id', '=', record.product_id.id),
                    ('id', '!=', record.id),
                    ('state', '!=', 'canceled')
                ])
                if existing:
                    raise ValidationError(
                        _('Serial number %s already exists for product %s') % 
                        (record.name, record.product_id.display_name)
                    )

    @api.constrains('product_qty', 'tracking')
    def _check_serial_quantity(self):
        """Validate quantity for serial numbers"""
        for record in self:
            if record.tracking == 'serial' and record.product_qty != 1.0:
                raise ValidationError(
                    _('Serial numbers must have quantity = 1')
                )

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to validate tracking type"""
        records = super().create(vals_list)
        for record in records:
            if record.tracking == 'none':
                raise UserError(
                    _('Product %s does not use lot/serial tracking') % 
                    record.product_id.display_name
                )
        return records

    def action_confirm(self):
        """Confirm the preassigned lots"""
        for record in self:
            if record.state != 'draft':
                continue
            record.write({
                'state': 'confirmed',
                'date_confirmed': fields.Datetime.now()
            })

    def action_create_stock_lot(self):
        """Create stock lot if it doesn't exist"""
        for record in self:
            if not record.stock_lot_id:
                lot = self.env['stock.lot'].create({
                    'name': record.name,
                    'product_id': record.product_id.id,
                    'company_id': record.purchase_order_id.company_id.id,
                })
                record.stock_lot_id = lot.id

    def action_mark_received(self):
        """Mark as received"""
        self.write({
            'state': 'received',
            'date_received': fields.Datetime.now()
        })

    def name_get(self):
        """Custom display name"""
        result = []
        for record in self:
            name = f"[{record.product_id.default_code or ''}] {record.name}"
            result.append((record.id, name))
        return result
