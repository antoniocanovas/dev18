# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class FscAuditLine(models.Model):
    _name = 'fsc.audit.line'
    _description = 'FSC audit line'


    name = fields.Char('Name' , related='material_id.alias')
    fsc_audit_id = fields.Many2one('fsc.audit', string='FSC Audit')

    material_id = fields.Many2one('product.material', string='Material')
    fsc_audit_product_ids = fields.One2many('fsc.audit.product', 'fsc_audit_line_id',
                                            string='Products', help='Products details')
    raw_fsc_format_id = fields.Many2one('product.attribute.value', string='Group', store=True)

    raw_stock_start_vol = fields.Float('Raw start stock')
    raw_purchase_vol = fields.Float('Qty', help='Purchases vol')
    raw_stock_final_vol = fields.Float('Raw final stock')
    raw_consumed_vol = fields.Float('Raw consumed', compute='_get_raw_consumed_vol')

    final_fsc_format_id = fields.Many2one('product.attribute.value', string='Final group')
    final_sale_vol = fields.Float('Sold', compute='_get_final_sold_qty')
    final_no_tracking_vol = fields.Float('No tracking')
    final_efficiency = fields.Float('FC', help='Final efficiency of tracking products')

    def _get_final_sold_qty(self):
        for rec in self:
            rec['final_sale_vol'] = sum(rec.fsc_audit_product_ids.mapped('sale_vol'))

    @api.depends('raw_stock_start_vol','raw_purchase_vol','raw_stock_final_vol')
    def _get_raw_consumed_vol(self):
        for rec in self:
            rec['raw_consumed_vol'] = rec.raw_stock_start_vol + rec.raw_purchase_vol - rec.raw_stock_final_vol

    """
    Para usar después (funciona): on_hand_a_fecha = record.with_context(to_date=today).qty_available
    """