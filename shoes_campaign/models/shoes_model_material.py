# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ShoesModelMaterial(models.Model):
    _name = 'shoes.model.material'
    _description = 'Shoes model material'

    name = fields.Char('Manufacturer Ref')
    material_id = fields.Many2one('product.material', string='Material')
    shoes_last_id = fields.Many2one('shoes.last', string='Last')
    shoes_product_tmpl_id = fields.Many2one('product.template', string='Product')
    task_id = fields.Many2one('project.task', string='Task')
    project_id = fields.Many2one(related='task_id.project_id')
