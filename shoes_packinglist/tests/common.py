from odoo.tests.common import TransactionCase


class PackingListCommon(TransactionCase):
    """Shared fixtures for shoes_packinglist tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        # Shipping agent partner
        cls.partner = cls.env["res.partner"].create({"name": "Test Shipping Agent"})

        # Product with lot tracking
        cls.product = cls.env["product.product"].create(
            {
                "name": "Test Shoe Model",
                "type": "consu",
                "tracking": "lot",
            }
        )

        # Lots
        cls.lot1 = cls.env["stock.lot"].create(
            {
                "name": "LOT001",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.lot2 = cls.env["stock.lot"].create(
            {
                "name": "LOT002",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.lot3 = cls.env["stock.lot"].create(
            {
                "name": "LOT003",
                "product_id": cls.product.id,
                "company_id": cls.env.company.id,
            }
        )

        # Warehouse / picking type
        cls.warehouse = cls.env["stock.warehouse"].search([], limit=1)
        cls.supplier_loc = cls.env.ref("stock.stock_location_suppliers")
        cls.stock_loc = cls.warehouse.lot_stock_id

        # Container (no lines yet)
        cls.container = cls.env["purchase.container"].create(
            {
                "code": "CONT001",
                "shipping_agent_id": cls.partner.id,
            }
        )

    def _make_incoming_picking(self, lots):
        """
        Create a confirmed incoming picking with one move per lot.
        Returns (picking, {lot_name: move_line}) for easy access in tests.
        """
        picking = self.env["stock.picking"].create(
            {
                "partner_id": self.partner.id,
                "picking_type_id": self.warehouse.in_type_id.id,
                "location_id": self.supplier_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        move = self.env["stock.move"].create(
            {
                "name": "Test Move",
                "picking_id": picking.id,
                "product_id": self.product.id,
                "product_uom_qty": float(len(lots)),
                "product_uom": self.product.uom_id.id,
                "location_id": self.supplier_loc.id,
                "location_dest_id": self.stock_loc.id,
            }
        )
        picking.action_confirm()
        move_lines = {}
        for lot in lots:
            ml = self.env["stock.move.line"].create(
                {
                    "move_id": move.id,
                    "picking_id": picking.id,
                    "product_id": self.product.id,
                    "lot_id": lot.id,
                    "quantity": 1.0,
                    "product_uom_id": self.product.uom_id.id,
                    "location_id": self.supplier_loc.id,
                    "location_dest_id": self.stock_loc.id,
                }
            )
            move_lines[lot.name] = ml
        return picking, move_lines
