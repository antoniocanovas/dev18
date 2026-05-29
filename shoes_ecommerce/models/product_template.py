# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def _is_combination_possible(self, combination, parent_combination=None, ignore_no_variant=False):
        if combination.filtered('is_custom'):
            return False
        return super()._is_combination_possible(combination, parent_combination, ignore_no_variant)
