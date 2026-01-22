# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"


    shoes_accesory_ids = fields.One2many(
        "shoes.accesory", "task_id",
        string="Accesories"
    )

    def shoes_create_product(self) -> dict:
        # Calculate the total cost of accessories
        accesories = self.env["shoes.accesory"].search(
            [("task_id", "=", self.id)]
        )
        accesories_cost = sum(
            acc.qty * acc.product_id.standard_price for acc in accesories
        )

        # Add the accessories cost to the exwork price before calling the original
        # method
        original_exwork = self.exwork
        self.exwork += accesories_cost

        # Call the original action_apply method
        res = super().shoes_create_product()

        # Restore the original exwork price to avoid permanently altering the
        # task's cost
        self.exwork = original_exwork

        return res