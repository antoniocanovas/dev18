# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class AssortmentPair(models.Model):
    _name = 'assortment.pair'
    _description = 'Assortment pair'

    name = fields.Char('Name', related='product_id.display_name')
    product_id = fields.Many2one('product.product', string='Product variant')
    product_tmpl_id = fields.Many2one('product.template', string='Product template', related='product_id.product_tmpl_id')
    bom_qty = fields.Integer('Bom units')
    qty = fields.Integer('Pairs', compute='_get_sml_qty')
    partner_id = fields.Many2one('res.partner', string='Partner')
    sml_id = fields.Many2one('stock.move.line', string='Stock move line')
    sml_qty = fields.Float(related='sml_id.quantity_product_uom')
    sm_id = fields.Many2one('stock.move', string='Stock move', related='sml_id.move_id')
    lot_id = fields.Many2one('stock.lot', string='Lot', related='sml_id.lot_id')

    # Calcula la cantidad de pares en función de la cantidad de la línea de movimiento de stock y la lista de materiales
    @api.depends('sml_id.quantity_product_uom', 'product_id')
    def _get_sml_qty(self):
        for record in self:
            factor = -1 if (record.sml_id.location_usage in ('internal', 'transit') and
                            record.sml_id.location_dest_usage not in ('internal', 'transit')) else 1
            record['qty'] = record.bom_qty * record.sml_qty * factor

    # CRON ACTION TO DELETE NULL ASSORTMENT PAIRS (revisar no es así porque los sm y sml son fijos, se van adicionando):
    def _delete_null_assortment_pair(self):
        null_assortmennt_pair = self.env['assortment.pair'].search([('sml_qty','=', 0)])
        null_assortmennt_pair.unlink()