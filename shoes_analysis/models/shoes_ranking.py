# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ShoesRanking(models.Model):
    _name = 'shoes.ranking'
    _description = 'Shoes Ranking'

    name = fields.Char(
        string='Name',
        store=True,
        compute='_compute_name',
    )

    shoes_campaign_id = fields.Many2one(
        'project.project',
        string='Campaign',
    )

    product_tmpl_id = fields.Many2one(
        comodel_name='product.template',
        string='Producto',
    )

    shoes_last_id = fields.Many2one(
        'shoes.last',
        string='Shoes last'
    )

    image = fields.Binary(
        string='Image',
        related='product_tmpl_id.image_256',
    )

    shoes_model_material_id = fields.Many2one(
        'shoes.model.material',
        string='Ref',
        related='product_tmpl_id.shoes_model_material_id',
    )

    shoes_analysis_id = fields.Many2one('shoes.analysis',)
    ranking = fields.Integer('Ranking')
    pairs_count_sale = fields.Integer('Sold')
    pairs_count_cancel = fields.Integer('Cancelled')
    pairs_count_net = fields.Integer('Net pairs')
    sale_net_amount = fields.Monetary('Net sale')
    currency_id = fields.Many2one(
        'res.currency', string='Currency', default=lambda self: self.env.user.company_id.currency_id)


    @api.depends('shoes_campaign_id', 'product_tmpl_id', 'shoes_last_id', 'ranking')
    def _compute_name(self):
        for record in self:
            record.name = record.shoes_campaign_id.name + " (" + str(record.ranking) + ")"
