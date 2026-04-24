from .common import PackingListCommon


class TestContainerLineCharCleaning(PackingListCommon):

    def test_lot_stripped_on_create(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "  LOT001  "}
        )
        self.assertEqual(line.lot, "LOT001")

    def test_tabulations_removed_on_create(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "name": "\tShoe Name\t"}
        )
        self.assertEqual(line.name, "Shoe Name")

    def test_all_char_fields_stripped_on_create(self):
        line = self.env["purchase.container.line"].create(
            {
                "container_id": self.container.id,
                "shoes_campaign": " Camp ",
                "name": " Name ",
                "color": " Black ",
                "purchase_order": " PO001 ",
                "assortment": " Assort ",
                "lot": " LOT001 ",
                "shippingmark": " SM01 ",
            }
        )
        self.assertEqual(line.shoes_campaign, "Camp")
        self.assertEqual(line.name, "Name")
        self.assertEqual(line.color, "Black")
        self.assertEqual(line.purchase_order, "PO001")
        self.assertEqual(line.assortment, "Assort")
        self.assertEqual(line.lot, "LOT001")
        self.assertEqual(line.shippingmark, "SM01")

    def test_char_fields_stripped_on_write(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        line.write({"lot": "  LOT002  ", "name": "  Shoe  "})
        self.assertEqual(line.lot, "LOT002")
        self.assertEqual(line.name, "Shoe")

    def test_empty_char_fields_not_modified(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001", "name": False}
        )
        self.assertFalse(line.name)

    def test_whitespace_only_char_field_becomes_false(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001", "name": "   "}
        )
        self.assertFalse(line.name)

    def test_numeric_fields_not_affected(self):
        line = self.env["purchase.container.line"].create(
            {
                "container_id": self.container.id,
                "lot": "LOT001",
                "pairs": 12.0,
                "assortment_gross_weight": 5.5,
            }
        )
        self.assertEqual(line.pairs, 12.0)
        self.assertEqual(line.assortment_gross_weight, 5.5)


class TestContainerO2M(PackingListCommon):

    def test_container_has_container_line_ids(self):
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        self.assertIn(line, self.container.container_line_ids)

    def test_line_deleted_when_container_deleted(self):
        local_container = self.env["purchase.container"].create(
            {"code": "CONT_CASCADE", "shipping_agent_id": self.partner.id}
        )
        line = self.env["purchase.container.line"].create(
            {"container_id": local_container.id, "lot": "LOT001"}
        )
        line_id = line.id
        local_container.unlink()
        self.assertFalse(self.env["purchase.container.line"].browse(line_id).exists())
