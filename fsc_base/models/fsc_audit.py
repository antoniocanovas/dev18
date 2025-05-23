# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api
from odoo.exceptions import UserError

class FscAudit(models.Model):
    _name = 'fsc.audit'
    _description = 'FSC Audit'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    name = fields.Char('Name', translate=True, tracking=True)
    auditor_id = fields.Many2one('res.partner', string='Auditor', tracking=True)
    audit_date = fields.Date(string='Audit Date', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], string='Status', default='draft', tracking=True)
    date_from = fields.Date('From')
    date_to   = fields.Date('To')
    notes = fields.Html('Comments',  copy=False , translate=True)
    line_ids = fields.One2many('fsc.audit.line','fsc_audit_id', string='Lines')

    def compute_fsc_audit(self):
        self.line_ids.unlink()
        # Objetivo es conseguir el rendimiento por MATERIAL COMPRADO indicando formato origen:
        fsc_products = self.env['product.product'].search([('wood_tracking','=',True),('is_fsc','=',True)])
        fsc_materials = fsc_products.material_id

        for mat in fsc_materials:
            # Buscar los formatos de los productos vendidos de cada material, que sean de origen FSC (sml):
            sml_sold = self.env['stock.move.line'].search([
                ('location_dest_id.usage','=','customer'),
                ('lot_id.material_id','=', mat.id,),
                ('product_id','in',fsc_products.ids),
            ])
            sml_products = sml_sold.product_id
            sml_fsc_values = sml_products.fsc_format_value_id
            for value in sml_fsc_values:
                sml_lots = sml_sold.lot_id
                sml_origin_values = sml_lots.fsc_origin_format_value_id
                for origin_value in sml_origin_values:
                    # Para cada valor de formato origen y destino una línea principal vacía:
                    new_audit_line = self.env['fsc.audit.line'].create({
                        'material_id': mat.id,
                        'fsc_audit_id': self.id,
                        'raw_fsc_format_id': origin_value.id,
                        'final_fsc_format_id': value.id,
                    })
                    # Busco los productos vendidos con origin_value de este bucle:
                    products_origin_value = set()
                    for lot in sml_lots:
                        if lot.fsc_origin_format_value_id == origin_value:
                            products_origin_value.add(lot.product_id)

                    for pov in products_origin_value:
                        # calcular volumen vendido desde los lotes anteriores:
                        volume = 0
                        for sml_pov in sml_sold:
                            if sml_pov.product_id == pov:
                                volume += sml_pov.qty_done * sml_pov.product_id.volume

                        # Crear fsc.audit.product(s) y completar la unificada anterior en fsc.audit.line:
                        self.env['fsc.audit.product'].create({
                            'fsc_audit_line_id': new_audit_line.id,
                            'product_id': pov.id,
                            'volume_sold': volume,
                            #'purchase_qty': ,
                            #'stock_start_qty':,
                            #'stock_final_qty':,
                            'fsc_format_id': value.id,
                        })
                    # Incrementar valores para tras el bucle completar new_audit_line (o hacerlos computados)
                    new_audit_line.write({
                        # 'fsc_audit_product_ids': ,
                        # 'raw_product_qty': ,
                        # 'raw_consumed' = fields.Float('Raw consumed')
                        # 'raw_stock' = fields.Float('Raw stock')
                        # 'final_fsc_format_id' = fields.Char('Final group')
                        # 'final_sold_qty' = fields.Float('Sold')
                        # 'final_no_tracking' = fields.Float('No tracking')
                        # 'final_efficiency'
                    })

                    #raise UserError(products_origin_value)

        return True
