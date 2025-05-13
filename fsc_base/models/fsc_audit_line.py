# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class FscAuditLine(models.Model):
    _name = 'fsc.audit.line'
    _description = 'FSC audit line'


    name = fields.Char('Name' , related='raw_product_id.name')
    fsc_audit_id = fields.Many2one('fsc.audit', string='FSC Audit')

    raw_product_id = fields.Many2one('product.product', string='Product', help='Purchased product')
    raw_product_qty = fields.Float('Qty', help='Purchased qty')
    raw_fsc_format_id = fields.Char(related='raw_product_id.fsc_format_value_id.name', string='Group')
    raw_scientific_name = fields.Char(related='raw_product_id.material_id.alias')
    raw_consumed = fields.Float('Raw consumed')
    raw_stock = fields.Float('Raw stock')
    final_fsc_format_id = fields.Char('Final group')
    final_sold_qty = fields.Float('Sold')
    final_no_tracking = fields.Float('No tracking')
    final_efficiency = fields.Float('FC', help='Final efficiency of tracking products')
