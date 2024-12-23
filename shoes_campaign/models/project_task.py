# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api
from odoo.exceptions import UserError

class ProjectTask(models.Model):
    _inherit = "project.task"

    is_shoes_campaign = fields.Boolean('Is shoes campaign', related='project_id.is_shoes_campaign')

    # Datos comunes para creación de productos desde tareas:

    product_brand_id = fields.Many2one('product.brand', related='project_id.product_brand_id')
    manufacturer_id = fields.Many2one('res.partner', string='Manufacturer')
    shoes_last_id = fields.Many2one('shoes.last', string='Last')
    code = fields.Char('Code')
    gender = fields.Selection(
        [("man", "Man"), ("woman", "Woman"), ("unisex", "Unisex")],
        string="Gender",
        copy=True,
        store=True,
    )

    shoes_pair_weight_id = fields.Many2one(
        "shoes.pair.weight", string="Pair Weight", default=False
    )

    shoes_model_material_ids = fields.One2many('shoes.model.material', 'task_id', string='Materials')

    @api.depends('shoes_model_material_ids.shoes_product_tmpl_id')
    def _get_pending_product_material_ids(self):
        for record in self:
            materials = set()
            for li in record.shoes_model_material_ids:
                if not li.shoes_product_tmpl_id.id:
                    materials.add(li.material_id.id)
            record['pending_product_material_ids'] = [(6,0,materials)]
    pending_product_material_ids = fields.Many2many('product.material', string='Pending materials',
                                                    compute='_get_pending_product_material_ids',
                                                    help='Pending product materials creation.')

    intrastat_duty_id = fields.Many2one('intrastat.duty', string='Duty estimation', copy=False)

    @api.constrains('create_date')
    def task_code_sequence(self):
        prefix = self.project_id.task_code_prefix
        seq = self.project_id.task_code_sequence
        code = prefix + str(seq + 1000)[-3:]
        self.code = code
        self.project_id.task_code_sequence = seq +1