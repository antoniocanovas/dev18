# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        """
        Asegurar que sale_line_id se propague a través de stock rules.
        
        Este método define qué campos personalizados deben mantenerse
        cuando se copian o procesan stock moves a través de reglas de stock.
        """
        fields = super()._get_custom_move_fields()
        if 'sale_line_id' not in fields:
            fields += ['sale_line_id']
        return fields

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        """
        Mantener sale_line_id al copiar moves en push rules.
        
        Cuando una regla de push crea un nuevo move basado en otro,
        necesitamos mantener la referencia a la línea de venta original.
        """
        res = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        
        if move_to_copy.sale_line_id:
            res['sale_line_id'] = move_to_copy.sale_line_id.id
        
        return res
