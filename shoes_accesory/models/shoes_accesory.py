# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api


class ShoesAccesory(models.Model):
    _name = "shoes.accesory"
    _description = "Shoes accesory"

    # Required:
    name = fields.Char("Name", translate=True, compute='_compute_name')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Integer('Qty', default=2)
    task_id = fields.Many2one('project.task', string='Model')

    # Related:
    manufacturer_id = fields.Many2one(
        'res.partner', store=True,
        related='task_id.manufacturer_id'
    )
    manufacturer_location_id = fields.Many2one(
        'stock.location', store=True,
        related='manufacturer_id.property_stock_customer'
    )
    shoes_campaign_id = fields.Many2one(
        'project.project', string='Campaign', store=True,
        related='task_id.project_id'
    )

    # Computed:
    pairs_campaign_sold = fields.Integer('Sold pairs', compute='_compute_pairs_campaign_sold')
    pairs_campaign_pending = fields.Integer('Pending pairs', compute='_compute_pairs_campaign_pending')
    accesory_campaign_sold_qty = fields.Float('Sold accesories', compute='_compute_accesory_campaign_sold_qty')
    accesory_campaign_pending_qty = fields.Float('Pending accesories', compute='_compute_accesory_campaign_pending_qty')
    accesory_manufacturer_stock = fields.Float('Manufacturer stock', help='Enviados menos producidos', compute='_compute_accesory_manufacturer_stock')
    accesory_stock = fields.Float('Stock', related='product_id.qty_available', store=True)
    accesory_supplier_pending = fields.Float('Assigned', compute='_compute_accesory_supplier_pending')
    accesory_manufacturer_status = fields.Float('Manufacturer Status', compute='_compute_accesory_manufacturer_status')

    @api.depends('product_id', 'qty')
    def _compute_name(self):
        for record in self:
            if record.product_id:
                record.name = record.product_id.name + " (" + str(record.qty) + ")"
            else:
                record.name = ''

    @api.depends('task_id')
    def _compute_pairs_campaign_sold(self):
        for record in self:
            if not record.task_id:
                record.pairs_campaign_sold = 0
                continue
            domain = [
                ('state', '=', 'sale'),
                ('product_id.shoes_task_id', '=', record.task_id.id),
                '|',
                ('product_id.is_pair', '=', True),
                ('product_id.is_assortment', '=', True)
            ]
            sold_lines = self.env['sale.order.line'].search(domain)
            record.pairs_campaign_sold = sum(sold_lines.mapped('pairs_count'))

    @api.depends('task_id')
    def _compute_pairs_campaign_pending(self):
        for record in self:
            if not record.task_id:
                record.pairs_campaign_pending = 0
                continue
            domain = [
                ('state', '=', 'sale'),
                ('product_id.shoes_task_id', '=', record.task_id.id),
                '|',
                ('product_id.is_pair', '=', True),
                ('product_id.is_assortment', '=', True)
            ]
            order_lines = self.env['sale.order.line'].search(domain)
            total_pending_pairs = 0
            for line in order_lines:
                pending_qty = line.product_uom_qty - line.qty_delivered
                if pending_qty > 0 and line.product_uom_qty > 0:
                    proportion = pending_qty / line.product_uom_qty
                    total_pending_pairs += proportion * line.pairs_count
            record.pairs_campaign_pending = total_pending_pairs

    @api.depends('pairs_campaign_sold', 'qty')
    def _compute_accesory_campaign_sold_qty(self):
        for record in self:
            record.accesory_campaign_sold_qty = record.pairs_campaign_sold * record.qty

    @api.depends('pairs_campaign_pending', 'qty')
    def _compute_accesory_campaign_pending_qty(self):
        for record in self:
            record.accesory_campaign_pending_qty = record.pairs_campaign_pending * record.qty

    @api.depends('product_id', 'manufacturer_location_id')
    def _compute_accesory_supplier_pending(self):
        StockMove = self.env['stock.move']
        for record in self:
            if not record.product_id or not record.manufacturer_location_id:
                record.accesory_supplier_pending = 0.0
                continue

            # Calculate the quantity of the product in moves that are 'assigned'
            # and destined for the manufacturer's location, regardless of origin.
            assigned_domain = [
                ('product_id', '=', record.product_id.id),
                ('location_dest_id', '=', record.manufacturer_location_id.id),
                ('state', '=', 'assigned'),
            ]
            assigned_moves = StockMove.search(assigned_domain)
            record.accesory_supplier_pending = sum(assigned_moves.mapped('product_uom_qty'))

    @api.depends('product_id', 'task_id', 'manufacturer_id', 'manufacturer_location_id', 'qty')
    def _compute_accesory_manufacturer_stock(self):
        StockMove = self.env['stock.move']
        PurchaseOrderLine = self.env['purchase.order.line']
        for record in self:
            if not all([record.product_id, record.manufacturer_location_id, record.task_id, record.manufacturer_id]):
                record.accesory_manufacturer_stock = 0.0
                continue

            # 1. Find the date of the last inventory adjustment for the product in the manufacturer's location
            last_inventory_move = StockMove.search([
                ('product_id', '=', record.product_id.id),
                '|',
                '&', ('location_id', '=', record.manufacturer_location_id.id), ('location_dest_id.usage', '=', 'inventory'),
                '&', ('location_dest_id', '=', record.manufacturer_location_id.id), ('location_id.usage', '=', 'inventory'),
            ], order='date desc', limit=1)
            last_inventory_date = last_inventory_move.date or fields.Datetime.from_string('1970-01-01')

            # 2. Calculate accessories sent to manufacturer since that date
            sent_domain = [
                ('product_id', '=', record.product_id.id),
                ('location_dest_id', '=', record.manufacturer_location_id.id),
                ('state', '=', 'done'),
                ('date', '>', last_inventory_date),
            ]
            sent_moves = StockMove.search(sent_domain)
            sent_qty_since_inventory = sum(sent_moves.mapped('quantity'))

            # 3. Calculate accessories consumed by manufacturer since that date
            purchase_lines_domain = [
                ('order_id.partner_id', '=', record.manufacturer_id.id),
                ('product_id.shoes_task_id', '=', record.task_id.id),
                ('state', 'in', ['purchase', 'done']),
            ]
            purchase_lines = PurchaseOrderLine.search(purchase_lines_domain)
            
            total_pairs_received_since_inventory = 0
            for line in purchase_lines:
                # Find moves for received finished goods after the inventory date
                line_moves = line.move_ids.filtered(
                    lambda m: m.state == 'done' and m.date > last_inventory_date
                )
                qty_received_since_inventory = sum(line_moves.mapped('quantity'))
                if qty_received_since_inventory > 0:
                    total_pairs_received_since_inventory += qty_received_since_inventory * line.product_id.pairs_count
            
            consumed_qty_since_inventory = total_pairs_received_since_inventory * record.qty

            # 4. Final calculation
            record.accesory_manufacturer_stock = sent_qty_since_inventory - consumed_qty_since_inventory

    @api.depends('accesory_campaign_pending_qty', 'accesory_manufacturer_stock', 'accesory_supplier_pending')
    def _compute_accesory_manufacturer_status(self):
        for record in self:
            record.accesory_manufacturer_status = (record.accesory_manufacturer_stock + record.accesory_supplier_pending) - record.accesory_campaign_pending_qty
