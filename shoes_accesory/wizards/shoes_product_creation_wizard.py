# Copyright 2024 Punt Sistemes
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ShoesProductCreationWizard(models.TransientModel):
    _inherit = "shoes.product.creation.wizard"

    def action_apply(self):
        # Calculate the total cost of accessories
        accesories = self.env['shoes.accesory'].search([('task_id', '=', self.task_id.id)])
        accesories_cost = sum(acc.qty * acc.product_id.standard_price for acc in accesories)

        # Add the accessories cost to the exwork price before calling the original method
        original_exwork = self.task_id.exwork
        self.task_id.exwork += accesories_cost

        # Call the original action_apply method
        res = super(ShoesProductCreationWizard, self).action_apply()

        # Restore the original exwork price to avoid permanently altering the task's cost
        self.task_id.exwork = original_exwork

        return res
