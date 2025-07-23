# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models
import logging

_logger = logging.getLogger(__name__)


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
            _logger.debug(
                "Copying sale_line_id %s from move %s to new move via push rule",
                move_to_copy.sale_line_id.id, move_to_copy.id
            )
        
        return res

    def _run_buy(self, procurements):
        """
        Override con logging simplificado y manejo de errores robusto.
        """
        try:
            # Intento de logging seguro - si falla, continúa sin problemas
            count_with_sale = 0
            for procurement, rule in procurements:
                if (hasattr(procurement, 'values') and 
                    isinstance(procurement.values, dict) and 
                    procurement.values.get('sale_line_id')):
                    count_with_sale += 1
            
            if count_with_sale > 0:
                _logger.debug(
                    "Running buy rule for %d procurements with sale_line_id",
                    count_with_sale
                )
        except Exception as e:
            # Logging falla, pero no interrumpimos la funcionalidad principal
            _logger.warning("Could not log procurement info: %s", str(e))
        
        return super()._run_buy(procurements)


class ProcurementGroup(models.Model):
    _inherit = 'procurement.group'

    def run(self, procurements, raise_user_error=True):
        """
        Override con logging simplificado y manejo de errores robusto.
        """
        try:
            # Intento de logging seguro - si falla, continúa sin problemas
            count_with_sale = 0
            for procurement in procurements:
                if (hasattr(procurement, 'values') and 
                    isinstance(procurement.values, dict) and 
                    procurement.values.get('sale_line_id')):
                    count_with_sale += 1
            
            if count_with_sale > 0:
                _logger.debug(
                    "Processing %d procurements with sale_line_id in group run",
                    count_with_sale
                )
        except Exception as e:
            # Logging falla, pero no interrumpimos la funcionalidad principal
            _logger.warning("Could not log procurement group info: %s", str(e))
        
        return super().run(procurements, raise_user_error=raise_user_error)
