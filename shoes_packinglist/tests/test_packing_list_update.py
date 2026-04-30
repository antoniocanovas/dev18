from odoo.exceptions import UserError

from .common import PackingListCommon


class TestUpdateValidations(PackingListCommon):

    def test_error_when_no_shipping_agent(self):
        container = self.env["purchase.container"].create({"code": "CONT_NOAGENT"})
        self.env["purchase.container.line"].create(
            {"container_id": container.id, "lot": "LOT001"}
        )
        with self.assertRaises(UserError):
            container.action_update_from_packing_list()

    def test_error_when_no_packing_list_lines(self):
        container = self.env["purchase.container"].create(
            {"code": "CONT_NOLINES", "shipping_agent_id": self.partner.id}
        )
        with self.assertRaises(UserError):
            container.action_update_from_packing_list()

    def test_error_when_no_pending_pickings(self):
        # Container has agent + lines, but no incoming pickings for that partner
        other_partner = self.env["res.partner"].create({"name": "No Pickings Agent"})
        container = self.env["purchase.container"].create(
            {"code": "CONT_NOPICK", "shipping_agent_id": other_partner.id}
        )
        self.env["purchase.container.line"].create(
            {"container_id": container.id, "lot": "LOT001"}
        )
        with self.assertRaises(UserError):
            container.action_update_from_packing_list()


class TestLotMatching(PackingListCommon):

    def test_matched_lot_sets_move_id(self):
        picking, _ = self._make_incoming_picking([self.lot1])
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        self.container.action_update_from_packing_list()
        self.assertTrue(line.move_id)

    def test_unmatched_lot_returns_wizard(self):
        picking, _ = self._make_incoming_picking([self.lot1])
        self.env["purchase.container.line"].create(
            {
                "container_id": self.container.id,
                "lot": "LOT001",  # matched
            }
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": self.container.id,
                "lot": "LOTXXX",  # not in Odoo
            }
        )
        result = self.container.action_update_from_packing_list()
        self.assertEqual(result.get("res_model"), "packing.list.warning.wizard")

    def test_unmatched_lot_leaves_move_id_false(self):
        picking, _ = self._make_incoming_picking([self.lot1])
        unmatched_line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOTXXX"}
        )
        self.container.action_update_from_packing_list()
        self.assertFalse(unmatched_line.move_id)

    def test_lot_in_done_picking_not_matched(self):
        """Lots whose picking is already done must not be matched."""
        picking, _ = self._make_incoming_picking([self.lot1])
        # stock.picking.state is computed; force via moves
        picking.move_ids.write({"state": "done"})
        line = self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        # Need another pending picking or we get UserError (no pending pickings)
        self._make_incoming_picking([self.lot2])
        self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT002"}
        )
        result = self.container.action_update_from_packing_list()
        # LOT001 was in a done picking → unmatched → wizard
        self.assertEqual(result.get("res_model"), "packing.list.warning.wizard")
        self.assertFalse(line.move_id)

    def test_all_matched_no_wizard(self):
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2])
        self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT001"}
        )
        self.env["purchase.container.line"].create(
            {"container_id": self.container.id, "lot": "LOT002"}
        )
        result = self.container.action_update_from_packing_list()
        # No wizard — result is True (processing continues inline)
        self.assertNotIsInstance(result, dict)


class TestProcessUpdate(PackingListCommon):
    """Tests for _process_packing_list_update: splitting and metrics."""

    def _container_with_lines(self, lots_in_packing):
        """Helper: container with packing list lines for the given lot names."""
        container = self.env["purchase.container"].create(
            {"code": f"CONT_{lots_in_packing[0]}", "shipping_agent_id": self.partner.id}
        )
        for lot_name in lots_in_packing:
            self.env["purchase.container.line"].create(
                {
                    "container_id": container.id,
                    "lot": lot_name,
                    "assortment_gross_weight": 2.5,
                    "volume": 0.1,
                }
            )
        return container

    def test_complete_picking_gets_container_id(self):
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2])
        container = self._container_with_lines(["LOT001", "LOT002"])
        container.action_update_from_packing_list()
        self.assertEqual(picking.container_id, container)

    def test_container_metrics_updated(self):
        self._make_incoming_picking([self.lot1, self.lot2])
        container = self._container_with_lines(["LOT001", "LOT002"])
        container.action_update_from_packing_list()
        # 2 lines × 2.5 kg = 5.0 kg
        self.assertAlmostEqual(container.weight, 5.0)
        # 2 lines × 0.1 = 0.2 volume
        self.assertAlmostEqual(container.volume, 0.2)
        # 2 lines
        self.assertEqual(container.package_qty, 2)

    def test_partial_picking_creates_backorder(self):
        # Picking has LOT001 + LOT002 + LOT003; packing list only has LOT001
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2, self.lot3])
        container = self._container_with_lines(["LOT001"])
        container.action_update_from_packing_list()

        # Original picking: container_id assigned
        self.assertEqual(picking.container_id, container)

        # Backorder created with LOT002 and LOT003
        backorder = self.env["stock.picking"].search(
            [("backorder_id", "=", picking.id)]
        )
        self.assertTrue(backorder, "Backorder picking should be created")
        backorder_lots = backorder.move_line_ids.mapped("lot_id.name")
        self.assertIn("LOT002", backorder_lots)
        self.assertIn("LOT003", backorder_lots)

    def test_partial_picking_container_picking_has_only_matched_lots(self):
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2, self.lot3])
        container = self._container_with_lines(["LOT001"])
        container.action_update_from_packing_list()

        container_lot_names = picking.move_line_ids.mapped("lot_id.name")
        self.assertIn("LOT001", container_lot_names)
        self.assertNotIn("LOT002", container_lot_names)
        self.assertNotIn("LOT003", container_lot_names)

    def test_metrics_only_include_matched_lines(self):
        """When wizard is bypassed via action_continue, only matched lines count."""
        self._make_incoming_picking([self.lot1])
        container = self.env["purchase.container"].create(
            {"code": "CONT_PARTIAL_M", "shipping_agent_id": self.partner.id}
        )
        # One matched line, one unmatched
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOT001",
                "assortment_gross_weight": 3.0,
                "volume": 0.2,
            }
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOTXXX",
                "assortment_gross_weight": 99.0,
                "volume": 99.0,
            }
        )
        result = container.action_update_from_packing_list()
        # Wizard returned for unmatched LOT
        self.assertEqual(result.get("res_model"), "packing.list.warning.wizard")
        # Simulate user clicking "Continue"
        wizard = self.env["packing.list.warning.wizard"].browse(result["res_id"])
        wizard.action_continue()
        # Only the matched line contributes to metrics
        self.assertAlmostEqual(container.weight, 3.0)
        self.assertAlmostEqual(container.volume, 0.2)
        self.assertEqual(container.package_qty, 1)

    def test_wizard_cancel_does_not_update_pickings(self):
        picking, _ = self._make_incoming_picking([self.lot1])
        container = self.env["purchase.container"].create(
            {"code": "CONT_WIZCANCEL", "shipping_agent_id": self.partner.id}
        )
        self.env["purchase.container.line"].create(
            {"container_id": container.id, "lot": "LOT001"}
        )
        self.env["purchase.container.line"].create(
            {"container_id": container.id, "lot": "LOTXXX"}
        )
        result = container.action_update_from_packing_list()
        wizard = self.env["packing.list.warning.wizard"].browse(result["res_id"])
        wizard.action_cancel()
        # Picking should not have container_id set
        self.assertFalse(picking.container_id)


class TestProductAndLotUpdate(PackingListCommon):
    """Tests for _update_product_weights_from_packing_list."""

    def _run_update_with_line(self, width=25.0, length=30.0, high=50.0,
                               gross=5.0, net=4.5, volume=0.5):
        """Helper: full update cycle with a single matched line."""
        picking, _ = self._make_incoming_picking([self.lot1])
        container = self.env["purchase.container"].create(
            {"code": "CONT_UPDATE", "shipping_agent_id": self.partner.id}
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOT001",
                "width": width,
                "length": length,
                "high": high,
                "assortment_gross_weight": gross,
                "assortment_net_weight": net,
                "volume": volume,
            }
        )
        container.action_update_from_packing_list()
        return container

    def test_width_length_high_written_to_product_product(self):
        self._run_update_with_line()
        self.assertEqual(self.product.width_length_high, "25×30×50")

    def test_lot_weight_written_from_packing_list(self):
        self._run_update_with_line(gross=5.0)
        self.assertAlmostEqual(self.lot1.weight, 5.0)

    def test_lot_net_weight_written_from_packing_list(self):
        self._run_update_with_line(net=4.5)
        self.assertAlmostEqual(self.lot1.net_weight, 4.5)

    def test_lot_volume_written_from_packing_list(self):
        self._run_update_with_line(volume=0.5)
        self.assertAlmostEqual(self.lot1.volume, 0.5)

    def test_lot_width_length_high_written_from_packing_list(self):
        self._run_update_with_line(width=25.0, length=30.0, high=50.0)
        self.assertEqual(self.lot1.width_length_high, "25×30×50")

    def test_lot_fields_not_written_when_no_dimensions(self):
        self._run_update_with_line(width=0.0, length=0.0, high=0.0)
        self.assertFalse(self.lot1.width_length_high)

    def test_two_lines_update_two_lots_independently(self):
        picking, _ = self._make_incoming_picking([self.lot1, self.lot2])
        container = self.env["purchase.container"].create(
            {"code": "CONT_TWO", "shipping_agent_id": self.partner.id}
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOT001",
                "assortment_gross_weight": 5.0,
                "assortment_net_weight": 4.5,
                "volume": 0.5,
                "width": 25.0,
                "length": 30.0,
                "high": 50.0,
            }
        )
        self.env["purchase.container.line"].create(
            {
                "container_id": container.id,
                "lot": "LOT002",
                "assortment_gross_weight": 6.0,
                "assortment_net_weight": 5.5,
                "volume": 0.6,
                "width": 26.0,
                "length": 31.0,
                "high": 51.0,
            }
        )
        container.action_update_from_packing_list()
        self.assertAlmostEqual(self.lot1.weight, 5.0)
        self.assertAlmostEqual(self.lot2.weight, 6.0)
        self.assertEqual(self.lot1.width_length_high, "25×30×50")
        self.assertEqual(self.lot2.width_length_high, "26×31×51")
