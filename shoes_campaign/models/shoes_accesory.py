# Copyright
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo import fields, models


class ShoesAccesory(models.Model):
    _name = "shoes.accesory"
    _description = "Shoes accesory"

    name = fields.Char("Name", translate=True, compute='_compute_name')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    qty = fields.Integer('Qty', default=2)
    task_id = fields.Many2one('project.task', string='Model')

    def _compute_name(self):
        for record in self:
            record.name = record.product_id.name + str(record.qty)
