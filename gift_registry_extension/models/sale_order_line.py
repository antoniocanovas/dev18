from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # --- Gift Registry Fields ---
    # The product_uom_qty field is used as the 'desired quantity' (qty_desired)

    qty_purchased = fields.Float(
        string='Quantity Purchased',
        default=0.0,
        copy=False,
        help="Total quantity of this item purchased by others against the gift registry."
    )

    qty_remaining = fields.Float(
        string='Quantity Remaining',
        compute='_compute_qty_remaining',
        store=True,
        help="Remaining quantity to be purchased (Desired - Purchased)."
    )

    # --- Fields for Purchases Against a Registry ---
    gift_registry_source_line_id = fields.Many2one(
        'sale.order.line',
        string='Gift Registry Source Line',
        copy=False,
        help="Link to the original gift registry line this purchase is for."
    )
    
    gift_registry_qty_remaining = fields.Float(
        string='Registry Qty Remaining',
        related='gift_registry_source_line_id.qty_remaining',
        readonly=True,
        store=False, # No need to store, it's for display
        help="Displays the remaining quantity on the source gift registry line."
    )

    @api.depends('product_uom_qty', 'qty_purchased')
    def _compute_qty_remaining(self):
        """
        Computes the remaining quantity for a gift registry line.
        For regular sale order lines, this will be zero.
        """
        for line in self:
            if line.order_id.is_gift_whishlist:
                line.qty_remaining = line.product_uom_qty - line.qty_purchased
            else:
                line.qty_remaining = 0

    @api.model_create_multi
    def create(self, vals_list):
        """
        When a sale order is confirmed or a PoS order is validated, if the lines
        are linked to a gift registry, update the purchased quantity on the
        source registry lines.
        """
        lines = super(SaleOrderLine, self).create(vals_list)
        # Check if the order is confirmed or comes from a PoS session
        for line in lines.filtered(lambda l: l.gift_registry_source_line_id and (l.order_id.state == 'sale' or l.order_id.session_id)):
            source_line = line.gift_registry_source_line_id
            # Use a write to avoid recursion and ensure atomicity
            source_line.write({
                'qty_purchased': source_line.qty_purchased + line.product_uom_qty
            })
        return lines

    def write(self, vals):
        """
        Handle updates to quantities on confirmed orders that are linked to a gift registry.
        """
        if 'product_uom_qty' in vals and self.env.context.get('updating_from_registry', False) is not True:
            # Check if the order is confirmed or comes from a PoS session
            for line in self.filtered(lambda l: l.gift_registry_source_line_id and (l.order_id.state == 'sale' or l.order_id.session_id)):
                # Calculate the difference in quantity
                qty_diff = vals['product_uom_qty'] - line.product_uom_qty
                source_line = line.gift_registry_source_line_id
                
                # Update the source line's purchased quantity
                new_purchased_qty = source_line.qty_purchased + qty_diff
                source_line.with_context(updating_from_registry=True).write({
                    'qty_purchased': new_purchased_qty
                })
        
        return super(SaleOrderLine, self).write(vals)
