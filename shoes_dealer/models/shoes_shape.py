# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models, api

class ShoesShape(models.Model):
    _name = 'shoes.shape'
    _description = 'Shoes MRP shape'

    name = fields.Char('Name')
    heel_type = fields.Char('Heel type')
    heel_height = fields.Float('Heel height')
    platform_height = fields.Float('Platform height')
    sole_material_main_id = fields.Many2one('product.material', string="Sole")
    sole_material_secondary_id = fields.Many2one('product.material', string="Sole 2nd")
    sole_material_main_percent = fields.Float('Sole main (%)')
    sole_material_secondary_percent = fields.Float('Sole 2nd (%)')
    insole_material_id = fields.Char('Insole')
    insole_material_percent = fields.Float('Insole material (%)')
    platform_material_id = fields.Many2one('product.material', string="Platform")
    platform_material_percent = fields.Float('Platform (%)')
    description = fields.Text('Description', translate=True)
