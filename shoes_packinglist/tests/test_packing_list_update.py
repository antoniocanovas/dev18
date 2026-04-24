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
