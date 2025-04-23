from odoo import _, api, fields, models
from odoo.exceptions import UserError

class ProductProduct(models.Model):
    _inherit = 'product.product'

    raw_efficiency = fields.Float('Raw efficiency', compute='_get_raw_efficiency_product_product')

    def _get_raw_efficiency_product_product(self):
        for record in self:
            raw, produced, efficiency = 0, 0, 1
            lots = self.env['stock.lot'].search([
                ('product_id','=',record.id),
                ('initial_received_quantity_computed','!=',0),
                ('product_id.fsc_tracking','=',True),
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
    fsc_mix_estimation = fields.Boolean(related='material_id.fsc_mix_estimation')
    fsc_type = fields.Selection(
        [("fsc", "FSC"), ("mix_credit", "Mix credit"), ("recycled", "Recycled"), ("mix_recycled", "Mix recycled")],
        string="FSC Type",
        copy=True,
    )
    fsc_percentage = fields.Float('FSC Percentage (%)')

    raw_efficiency_pt = fields.Float('Raw efficiency', compute='_get_raw_efficiency_product_template')

    def _get_raw_efficiency_product_template(self):
        for record in self:
            rawvolume, producedvolume, efficiency = 0, 0, 1
            lots = self.env['stock.lot'].search([
                ('product_id.product_tmpl_id','=',record.id),
                ('initial_received_quantity_computed','!=',0),
                ('product_id.fsc_tracking','=',True),
            ])
            for lot in lots:
                rawvolume += lot.initial_received_quantity_computed * lot.product_id.volume
                producedvolume += lot.initial_received_quantity_computed * lot.product_id.volume * lot.raw_efficiency / 100
            if rawvolume != 0:
                efficiency = producedvolume / rawvolume
            record['raw_efficiency_pt'] = efficiency * 100

    @api.constrains('fsc_type','fsc_percentage')
    def _check_fsc_percentage(self):
        if self.fsc_type in ['mix_credit','mix_recycled'] and not self.fsc_mix_estimation and self.fsc_percentage <= 0:
            raise UserError('FSC percentage must be greater than 0 in mixed types !!')
