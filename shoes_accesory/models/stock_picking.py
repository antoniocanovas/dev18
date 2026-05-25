# Copyright 2024 Punt Sistemes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self) -> bool | dict:
        # First, call the original method to validate the picking
        res = super().button_validate()

        # Now, process the consumption of accessories
        for picking in self:
            # --- Validation Checks ---
            # 1. Must be an outgoing picking
            if picking.picking_type_code != "outgoing":
                continue
            # 2. Must originate from a Purchase Order
            if not picking.purchase_id:
                continue
            # 3. Must come from a known manufacturer's location
            all_manufacturer_locations = (
                self.env["shoes.accesory"].search([]).mapped("manufacturer_location_id")
            )
            if picking.location_id not in all_manufacturer_locations:
                continue

            # Find the virtual production location
            production_location = self.env.ref(
                "stock.stock_location_production", raise_if_not_found=False
            )
            if not production_location:
                continue

            for move in picking.move_ids_without_package:
                # --- Further Validation per Move Line ---
                # 4. Product must be a pair or an assortment
                if not (move.product_id.is_pair or move.product_id.is_assortment):
                    continue
                # 5. Product must have a task to find its accessories
                if not move.product_id.shoes_task_id:
                    continue

                # Find all accessories linked to this shoe's task
                accessories = self.env["shoes.accesory"].search(
                    [("task_id", "=", move.product_id.shoes_task_id.id)]
                )

                for accessory in accessories:
                    # Calculate the total quantity of the accessory to consume
                    pairs_count = getattr(move.product_id, "pairs_count", 1)
                    consumed_qty = move.quantity * pairs_count * accessory.qty

                    if consumed_qty > 0:
                        # Create and validate an internal stock move for the consumption
                        self.env["stock.move"].create(
                            {
                                "name": f"Consumption for {move.product_id.name}",
                                "product_id": accessory.product_id.id,
                                "product_uom_qty": consumed_qty,
                                "product_uom": accessory.product_id.uom_id.id,
                                "location_id": picking.location_id.id,
                                "location_dest_id": production_location.id,
                            }
                        )._action_done()

        return res
