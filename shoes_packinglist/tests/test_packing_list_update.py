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
