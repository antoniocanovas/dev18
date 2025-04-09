from odoo import _, api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    raw_efficiency = fields.Float('Raw efficiency', compute='_get_raw_efficiency')

    @api.depends('state')
    def _get_raw_efficiency(self):
        for record in self:
            rawvolume, producedvolume, efficiency = 0, 0, 1
            # move_raw_ids son entradas, move_finished_ids son todas las salidas, move_byproduct_ids sólo los subproductos:
            for sm in record.move_raw_ids:
                for sml in sm.move_line_ids:
                    factor = 1
                    # Buscamos la orden de producción para este producto y lote por si encontramos eficiencia previa:
                    smlproduced = self.env['stock.move.line'].search([
                        ('product_id', '=', sml.product_id.id),
                        ('move_id.production_id', '!=', False),
                        ('location_id.usage', '=', 'production'),
                        ('lot_id', '=', sml.lot_id.id),
                    ], limit=1)
                    if smlproduced.id and smlproduced.move_id.production_id.raw_efficiency > 0:
                        factor = smlproduced.move_id.production_id.raw_efficiency / 100
                    rawvolume += sml.product_id.volume * sml.quantity / factor
            # Si un producto está marcado como desecho no cuenta como volumen producido:
            for li in record.move_finished_ids:
                if li.product_id.fsc_scrap == False:
                    producedvolume += li.product_id.volume * li.quantity
            if rawvolume > 0:
                efficiency = producedvolume / rawvolume * 100
            record['raw_efficiency'] = efficiency


