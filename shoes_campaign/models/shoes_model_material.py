# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models, api

class ShoesModelMaterial(models.Model):
    _name = 'shoes.model.material'
    _description = 'Shoes model material'

    name = fields.Char('Name', store=True, compute='_get_name')
    manufacturer_ref = fields.Char('Manufacturer Ref')
    material_id = fields.Many2one('product.material', string='Material')
    shoes_last_id = fields.Many2one('shoes.last', string='Last')
    shoes_product_tmpl_id = fields.Many2one('product.template', string='Product')
    task_id = fields.Many2one('project.task', string='Task')
    shoes_campaign_id = fields.Many2one(related='task_id.project_id')

    @api.depends('material_id','manufacturer_ref')
    def _get_name(self):
        for record in self:
            name = ""
            if record.material_id: name = record.material_id.name
            if record.manufacturer_ref: name += " (" + record.manufacturer_ref + ")"
            record['name'] = name