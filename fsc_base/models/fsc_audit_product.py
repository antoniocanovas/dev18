# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class FscAuditProduct(models.Model):
    _name = 'fsc.audit.product'
    _description = 'FSC audit product'


    name = fields.Char('Name' , related='product_id.name')
    fsc_audit_line_id = fields.Many2one('fsc.audit.line', string='Line')
    fsc_audit_id = fields.Many2one(related='fsc_audit_line_id.fsc_audit_id', string='FSC Audit')

    product_id = fields.Many2one('product.product', string='Product', help='Product')
    sale_vol = fields.Float('Sales Volume')
    fsc_format_id = fields.Char(related='product_id.fsc_format_value_id.name', string='Group')

    # PROBABLEMENTE FALTAN CAMPOS PARA RELACIONES O2M PARA LOS PRODUCTOS ORIGEN QUE HAN DE GUARDAR LA MISMA INFO
    # fsc_audit_raw_line_id y fsc_audit_sale_line_id en vez de fsc_audit_line_id