# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ProductAttributeCustomValue(models.Model):
    _inherit = 'product.attribute.custom.value'

    # Validación de datos custom introducidos pasa a líne de venta para evitar que el chequeo sea al guardar el pedido.
#    assortment_pair = fields.Char(related='sale_order_line_id.assortment_pair')
#    pairs_count = fields.Integer(related='sale_order_line_id.pairs_custom_assortment_count')
