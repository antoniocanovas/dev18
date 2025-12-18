from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    is_gift_whishlist = fields.Boolean(
        string='Is a Gift Registry',
        default=False,
        copy=False,
        help="Check this box if this sale order is a gift registry. It will be visible in the PoS and Sales modules for purchasing against."
    )

    def action_load_gift_registry(self):
        """
        This action finds all gift registry lines for the order's customer
        and adds them to the current sales order with a quantity of 0.
        The user can then decide which items to purchase.
        """
        self.ensure_one()
        if not self.partner_id:
            return

        # Find all open gift registry lines for this partner from confirmed registries
        source_lines = self.env['sale.order.line'].search([
            ('order_id.partner_id', '=', self.partner_id.id),
            ('order_id.is_gift_whishlist', '=', True),
            ('qty_remaining', '>', 0),
            ('order_id.state', 'in', ['sale', 'done'])
        ])

        # Exclude lines that are already on the current order to avoid duplicates
        existing_source_ids = self.order_line.mapped('gift_registry_source_line_id').ids
        lines_to_add = source_lines.filtered(lambda l: l.id not in existing_source_ids)

        new_lines_vals = []
        for line in lines_to_add:
            new_lines_vals.append({
                'order_id': self.id,
                'product_id': line.product_id.id,
                'product_uom_qty': 0.0,  # Set initial quantity to 0
                'gift_registry_source_line_id': line.id,
            })
        
        if new_lines_vals:
            self.env['sale.order.line'].create(new_lines_vals)
        
        # Return True to reload the view and show the new lines
        return True

    @api.model
    def update_gift_registry_from_pos(self, registry_order_id, order_lines_data, all_registry_line_ids_to_check):
        """
        This method is called from the Point of Sale to synchronize the gift registry
        with the PoS order.
        """
        registry_order = self.browse(registry_order_id)
        if not registry_order.exists() or not registry_order.is_gift_whishlist:
            return {'error': 'Gift registry not found.'}

        registry_lines = registry_order.order_line
        registry_lines_by_product = {line.product_id.id: line for line in registry_lines}
        
        lines_to_check_set = set(all_registry_line_ids_to_check)

        # Update existing lines and create new ones
        for line_data in order_lines_data:
            product_id = line_data['product_id']
            qty = line_data['qty']

            if product_id in registry_lines_by_product:
                # Update existing line
                line = registry_lines_by_product[product_id]
                line.write({'product_uom_qty': qty})
                if line.id in lines_to_check_set:
                    lines_to_check_set.remove(line.id)
            else:
                # Create new line
                self.env['sale.order.line'].create({
                    'order_id': registry_order.id,
                    'product_id': product_id,
                    'product_uom_qty': qty,
                    'price_unit': self.env['product.product'].browse(product_id).list_price,
                })

        # Remove lines that were deleted from the PoS cart
        lines_to_delete = self.env['sale.order.line'].browse(list(lines_to_check_set))
        for line in lines_to_delete:
            if line.qty_purchased == 0:
                line.unlink()

        return {'success': True, 'registry_name': registry_order.name}
