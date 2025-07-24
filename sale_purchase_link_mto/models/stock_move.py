# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


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
        
        return values
