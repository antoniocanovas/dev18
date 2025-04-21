from odoo import _, api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    raw_efficiency = fields.Float('Raw efficiency', compute='_get_raw_efficiency_product_product')

    def _get_raw_efficiency_product_product(self):
        for record in self:
            raw, produced, efficiency = 0, 0, 1
            lots = self.env['stock.lot'].search([
                ('product_id','=',record.id),
                ('initial_received_quantity_computed','!=',0),
                ('product_id.fsc_scrap','=',False),
            ])
            for lot in lots:
                raw += lot.initial_received_quantity_computed
                produced += lot.initial_received_quantity_computed * lot.raw_efficiency / 100
            if raw != 0:
                efficiency = produced / raw
            record['raw_efficiency'] = efficiency * 100

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    fsc_tracking = fields.Boolean(related='material_id.fsc_tracking')


    fsc_scrap = fields.Boolean('FSC Scrap', help='Not considered in MRP FSC efficiency when active.')
    raw_efficiency_pt = fields.Float('Raw efficiency', compute='_get_raw_efficiency_product_template')

    def _get_raw_efficiency_product_template(self):
        for record in self:
            rawvolume, producedvolume, efficiency = 0, 0, 1
            lots = self.env['stock.lot'].search([
                ('product_id.product_tmpl_id','=',record.id),
                ('initial_received_quantity_computed','!=',0),
                ('product_id.fsc_scrap','=',False),
            ])
            for lot in lots:
                rawvolume += lot.initial_received_quantity_computed * lot.product_id.volume
                producedvolume += lot.initial_received_quantity_computed * lot.product_id.volume * lot.raw_efficiency / 100
            if rawvolume != 0:
                efficiency = producedvolume / rawvolume
            record['raw_efficiency_pt'] = efficiency * 100
