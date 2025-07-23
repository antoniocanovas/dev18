# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.tests import Form, tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestMTOSalePurchaseLink(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        
        # Create vendor
        cls.vendor = cls.env['res.partner'].create({
            'name': 'Test Vendor MTO',
            'is_company': True,
            'supplier_rank': 1,
        })
        
        # Create customer
        cls.customer = cls.env['res.partner'].create({
            'name': 'Test Customer MTO',
            'is_company': True,
        })
        
        # Create MTO product with vendor
        cls.product_mto = cls.env['product.product'].create({
            'name': 'MTO Product Test',
            'type': 'product',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'route_ids': [
                (6, 0, [
                    cls.env.ref('stock.route_warehouse0_mto').id,
                    cls.env.ref('purchase_stock.route_warehouse0_buy').id
                ])
            ],
            'seller_ids': [(0, 0, {
                'partner_id': cls.vendor.id,
                'price': 100.0,
                'delay': 1,
            })],
        })

    def test_mto_sale_purchase_link(self):
        """Test that sale_line_id is properly set in purchase order lines for MTO products"""
        
        # Create sale order
        so_form = Form(self.env['sale.order'])
        so_form.partner_id = self.customer
        
        with so_form.order_line.new() as line:
            line.product_id = self.product_mto
            line.product_uom_qty = 5.0
            line.price_unit = 150.0
        
        sale_order = so_form.save()
        sale_line = sale_order.order_line[0]
        
        # Confirm sale order
        sale_order.action_confirm()
        
        # Run procurement scheduler
        self.env['procurement.group'].run_scheduler()
        
        # Find the generated purchase order line
        purchase_lines = self.env['purchase.order.line'].search([
            ('product_id', '=', self.product_mto.id),
            ('order_id.origin', 'ilike', sale_order.name)
        ])
        
        # Verify the link was created
        self.assertTrue(
            purchase_lines, 
            "No purchase order line was generated for MTO product"
        )
        
        purchase_line = purchase_lines[0]
        self.assertEqual(
            purchase_line.sale_line_id.id, 
            sale_line.id,
            f"sale_line_id not properly linked: expected {sale_line.id}, got {purchase_line.sale_line_id.id if purchase_line.sale_line_id else 'None'}"
        )
        
        self.assertEqual(
            purchase_line.sale_order_id.id,
            sale_order.id,
            "sale_order_id not properly computed from sale_line_id"
        )

    def test_mto_multiple_lines(self):
        """Test linking with multiple lines in same sale order"""
        
        # Create another MTO product
        product_mto_2 = self.env['product.product'].create({
            'name': 'MTO Product Test 2',
            'type': 'product',
            'categ_id': self.env.ref('product.product_category_all').id,
            'route_ids': [
                (6, 0, [
                    self.env.ref('stock.route_warehouse0_mto').id,
                    self.env.ref('purchase_stock.route_warehouse0_buy').id
                ])
            ],
            'seller_ids': [(0, 0, {
                'partner_id': self.vendor.id,
                'price': 200.0,
                'delay': 2,
            })],
        })
        
        # Create sale order with multiple lines
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [
                (0, 0, {
                    'product_id': self.product_mto.id,
                    'product_uom_qty': 3.0,
                    'price_unit': 150.0,
                }),
                (0, 0, {
                    'product_id': product_mto_2.id,
                    'product_uom_qty': 2.0,
                    'price_unit': 250.0,
                }),
            ],
        })
        
        sale_line_1 = sale_order.order_line[0]
        sale_line_2 = sale_order.order_line[1]
        
        # Confirm sale order
        sale_order.action_confirm()
        
        # Run procurement scheduler
        self.env['procurement.group'].run_scheduler()
        
        # Find purchase lines for each product
        po_line_1 = self.env['purchase.order.line'].search([
            ('product_id', '=', self.product_mto.id),
            ('order_id.origin', 'ilike', sale_order.name)
        ], limit=1)
        
        po_line_2 = self.env['purchase.order.line'].search([
            ('product_id', '=', product_mto_2.id),
            ('order_id.origin', 'ilike', sale_order.name)
        ], limit=1)
        
        # Verify both links
        self.assertTrue(po_line_1, "Purchase line for product 1 not found")
        self.assertTrue(po_line_2, "Purchase line for product 2 not found")
        
        self.assertEqual(po_line_1.sale_line_id.id, sale_line_1.id, "Product 1 not properly linked")
        self.assertEqual(po_line_2.sale_line_id.id, sale_line_2.id, "Product 2 not properly linked")

    def test_stock_move_procurement_values(self):
        """Test that stock moves properly propagate sale_line_id to procurement values"""
        
        # Create sale order
        sale_order = self.env['sale.order'].create({
            'partner_id': self.customer.id,
            'order_line': [(0, 0, {
                'product_id': self.product_mto.id,
                'product_uom_qty': 1.0,
                'price_unit': 100.0,
            })],
        })
        
        # Confirm to generate stock moves
        sale_order.action_confirm()
        
        # Find the stock move
        stock_moves = self.env['stock.move'].search([
            ('sale_line_id', '=', sale_order.order_line[0].id),
            ('product_id', '=', self.product_mto.id)
        ])
        
        self.assertTrue(stock_moves, "Stock move not found")
        
        stock_move = stock_moves[0]
        procurement_values = stock_move._prepare_procurement_values()
        
        # Verify that sale_line_id is in procurement values
        self.assertIn('sale_line_id', procurement_values, "sale_line_id not in procurement values")
        self.assertEqual(
            procurement_values['sale_line_id'], 
            sale_order.order_line[0].id,
            "Incorrect sale_line_id in procurement values"
        )
