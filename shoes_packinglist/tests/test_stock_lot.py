from odoo.tests.common import TransactionCase


class TestStockLotPackingListFields(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env["product.product"].create(
            {"name": "Test Shoe Lot", "type": "consu", "tracking": "lot"}
        )
        self.lot = self.env["stock.lot"].create(
            {
                "name": "LOT_TEST",
                "product_id": self.product.id,
                "company_id": self.env.company.id,
            }
        )

    def test_lot_has_weight_field(self):
        self.lot.write({"weight": 5.0})
        self.assertAlmostEqual(self.lot.weight, 5.0)

    def test_lot_has_net_weight_field(self):
        self.lot.write({"net_weight": 4.5})
        self.assertAlmostEqual(self.lot.net_weight, 4.5)

    def test_lot_has_volume_field(self):
        self.lot.write({"volume": 0.5})
        self.assertAlmostEqual(self.lot.volume, 0.5)

    def test_lot_has_width_length_high_field(self):
        self.lot.write({"width_length_high": "25×30×50"})
        self.assertEqual(self.lot.width_length_high, "25×30×50")

    def test_lot_fields_independent_from_product(self):
        self.lot.write({"weight": 5.0, "net_weight": 4.5, "volume": 0.5, "width_length_high": "25×30×50"})
        self.product.write({"weight": 99.0})
        self.assertAlmostEqual(self.lot.weight, 5.0)
