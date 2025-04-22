from odoo import _, api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    fsc_efficiency = fields.Float('FSC efficiency', store=True, compute='_get_fsc_efficiency')

    # Para control de purezo FSC hay que revisar materiales de entrada y asignar % a la orden de producción.
    # Si el material viene de otra orden => el de la orden; si es comprado hay tres opciones:
        # a) 100% si type es FSC,
        # b) El porcentaje estimado si el MATERIAL del PRODUCTO tiene este tratamiento
        # c) Porcentaje directo del producto si es type MIX y el material no es por porcentaje fijo.
    fsc_percentage = fields.Float('FSC percentage')

    @api.depends('state')
    def _get_fsc_efficiency(self):
        for record in self:
            rawvolume, producedvolume, efficiency = 0, 0, 1
            volxpercentfsc = 0
            # move_raw_ids son entradas, move_finished_ids son todas las salidas, move_byproduct_ids sólo los subproductos:
            for sm in record.move_raw_ids:
                if sm.product_id.material_id.fsc_tracking:
                    for sml in sm.move_line_ids:
                        factor = 1
                        # Buscamos la orden de producción para este producto y lote por si encontramos eficiencia previa:
                        smlproduced = self.env['stock.move.line'].search([
                            ('product_id', '=', sml.product_id.id),
                            ('move_id.production_id', '!=', False),
                            ('location_id.usage', '=', 'production'),
                            ('lot_id', '=', sml.lot_id.id),
                        ], limit=1)
                        if smlproduced.id and smlproduced.move_id.production_id.fsc_efficiency > 0:
                            factor = smlproduced.move_id.production_id.fsc_efficiency / 100
                        rawvolume += sml.product_id.volume * sml.quantity / factor

            # Si un producto está marcado como desecho no cuenta como volumen producido:
            for li in record.move_finished_ids:
                if li.product_id.material_id.fsc_tracking:
                    producedvolume += li.product_id.volume * li.quantity
            if rawvolume > 0:
                efficiency = producedvolume / rawvolume * 100
            record.write({'fsc_efficiency': efficiency})
