# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _inherit = 'res.company'

    shoes_sku_item_ids = fields.Many2many('shoes.product.sku.item', string='SKU Items', default=[(6,0,[1,2,3,4,5])])
    shoes_sku_update = fields.Boolean('Update on creation', default=True, help='Internal ref will be updated on pairs creation.')
    shoes_sku_sequence_id = fields.Many2one(
        'ir.sequence',
        string='SKU Sequence',
        default=lambda self: self.env.ref('shoes_product_sku.shoes_sku_sequence', raise_if_not_found=False),
    )

    # Parametrización para la cadena utilizada en la composición de la referencia interna del producto:
    shoes_code_product = fields.Selection([
        ('code','Code'),('name','Name'),('none','None')],
        string='Product code',
        default='code',
    )
    shoes_code_manufacturer = fields.Selection([
        ('code', 'Code'), ('name', 'Name'), ('none', 'None')],
        string='Manufacturer code',
        default='code',
    )
    shoes_code_color = fields.Selection([
        ('code','Code'),('name','Name'),('none','None')],
        string='Color code',
        default='code',
    )
    shoes_code_material = fields.Selection([
        ('code','Code'),('name','Name'),('none','None')],
        string='Material code',
        default='code',
    )
    shoes_code_campaign = fields.Selection([
        ('code','Code'),('name','Name'),('none','None')],
        string='Campaign code',
        default='name',
    )
    shoes_code_product_prefix = fields.Char(
        string='Product prefix',
        size=2,
    )
    shoes_code_manufacturer_prefix = fields.Char(
        string='Manufacturer prefix',
        size=2,
    )
    shoes_code_color_prefix = fields.Char(
        string='Color prefix',
        size=2,
    )
    shoes_code_material_prefix = fields.Char(
        string='Material prefix',
        size=2,
    )
    shoes_code_campaign_prefix = fields.Char(
        string='Campaign prefix',
        size=2,
    )

    #  Forzar que todos los parámetros posibles estén establecidos:
    @api.constrains('shoes_sku_item_ids')
    def _ensure_unique_sku(self):
        if len(self.shoes_sku_item_ids.ids) != 5:
            raise UserError('Include all codes to ensure an unique SKU per product.')

