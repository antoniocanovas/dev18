from odoo import _, api, fields, models
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    fsc_efficiency = fields.Float('FSC efficiency')

    # Para control de purezo FSC hay que revisar materiales de entrada y asignar % a la orden de producción.
    # Si el material viene de otra orden => el de la orden; si es comprado hay tres opciones:
        # a) 100% si type es FSC,
        # b) El porcentaje estimado si el MATERIAL del PRODUCTO tiene este tratamiento
        # c) Porcentaje directo del producto si es type MIX y el material no es por porcentaje fijo.
    fsc_percentage = fields.Float('FSC percentage')

    def _get_fsc_efficiency_and_percentage(self):
        for record in self:
            # Para el cálculo de eficiencia FSC en base a pérdidas por corte y desechos:
            rawvolume, producedvolume, efficiency = 0, 0, 1

            # Para el cálculo de porcentaje FSC en la entrada de producción que se guardará en el mrp.production:
            fscvolume, incomevolume  = 0, 0

            # move_raw_ids son entradas, move_finished_ids son todas las salidas, move_byproduct_ids sólo los subproductos:
            for sm in record.move_raw_ids:
                if sm.product_id.material_id.fsc_tracking:
                    for sml in sm.move_line_ids:
                        factor = 1
                        product = sml.product_id

                        # Para productos FSC 100%:
                        if product.fsc_type in ['fsc', 'recycled']:
                            fsc_percentage = 100
                        # Caso de que el % sea estimado y responsabilidad del cliente en compras y fabricaciones:
                        elif material.fsc_mix_estimation:
                            fsc_percentage = material.fsc_mix_percentage
                        # Caso de producto comprado con un % certificado de FSC pero el % cambiará al mezclar en fabricación:
                        elif not material.fsc_mix_estimation and product.fsc_type in ['mix_credit', 'mix_recycled']:
                            fsc_percentage = product.fsc_percentage

                        # Buscamos la orden de producción para este producto y lote por si encontramos eficiencia previa:
                        smlproduced = self.env['stock.move.line'].search([
                            ('product_id', '=', product.id),
                            ('move_id.production_id', '!=', False),
                            ('location_id.usage', '=', 'production'),
                            ('lot_id', '=', sml.lot_id.id),
                        ], limit=1)
                        if smlproduced.id and smlproduced.move_id.production_id.fsc_efficiency > 0:
                            factor = smlproduced.move_id.production_id.fsc_efficiency / 100

                            # Para el caso de productos que puedan fluctuar su certificación FSC:
                        if smlproduced.id and product.fsc_type in ['mix_credit', 'mix_recycled']:
                            fsc_percentage = smlproduced.move_id.production_id.fsc_percentage

                        rawvolume += product.volume * sml.quantity / factor
                        incomevolume += product.volume * sml.quantity
                        fscvolume += product.volume * sml.quantity * fsc_percentage / 100

            if incomevolume > 0:
                fsc_percentage = fscvolume / incomevolume * 100
                #print('fsc_percentage: ' + str(fsc_percentage) + " fscvolume: " + str(fscvolume)+ " incomevolume: " + str(incomevolume))

            # Si un producto está marcado como desecho no cuenta como volumen producido:
            for li in record.move_finished_ids:
                if li.product_id.material_id.fsc_tracking:
                    producedvolume += li.product_id.volume * li.quantity
            if rawvolume > 0:
                efficiency = producedvolume / rawvolume * 100
            record.write({'fsc_efficiency': efficiency, 'fsc_percentage':fsc_percentage})

    def _fsc_update_mrp_update(self):
        for rec in self:
            if rec.state not in ['draft']:
                # Actualizar datos de eficiencia:
                rec._get_fsc_efficiency_and_percentage()

                # Chequear si los productos finales son 100% FSC y los de entrada son también 100%:
                if rec.state == 'done' and rec.fsc_percentage < 100:
                    products = rec.finished_move_line_ids.product_id
                    product_names = ""
                    for product in products:
                        if product.fsc_type in ['fsc','recycled']:
                            product_names += "[" + product.name + "] "
                    if product_names != "":
                        raise UserError('Los productos a fabricar ' + product_names + ' requieren que todos materiales sean FSC 100%')
