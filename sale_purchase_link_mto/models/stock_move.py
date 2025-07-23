# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
import logging

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        """
        Añadir sale_line_id a los valores de procurement para mantener 
        la vinculación entre líneas de venta y compra en procesos MTO.
        
        Esta extensión asegura que cuando un stock.move genera un procurement,
        la información de la línea de venta original se propague hasta 
        la línea de compra resultante.
        """
        values = super()._prepare_procurement_values()
        
        # Si el move tiene sale_line_id, lo propagamos al procurement
        if self.sale_line_id:
            values['sale_line_id'] = self.sale_line_id.id
            _logger.debug(
                "Propagating sale_line_id %s from stock.move %s to procurement values",
                self.sale_line_id.id, self.id
            )
        
        return values

    def _action_confirm(self, merge=True, merge_into=False):
        """
        Override para debug - ayuda a rastrear el flujo de datos
        """
        result = super()._action_confirm(merge=merge, merge_into=merge_into)
        
        # Log para debugging en caso de problemas
        moves_with_sale = self.filtered('sale_line_id')
        if moves_with_sale:
            _logger.debug(
                "Confirmed %d stock moves with sale_line_id: %s", 
                len(moves_with_sale), 
                moves_with_sale.mapped('sale_line_id.id')
            )
        
        return result
