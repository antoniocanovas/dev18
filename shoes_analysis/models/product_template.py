# Copyright 2024 Punt Sistemes SL

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    shoes_ranking_ids = fields.One2many(
        'shoes.ranking',
        'product_tmpl_id',
        string='Ranking de ventas',
        help='Ranking de ventas por campaña'
    )

    shoes_assortment_ranking_ids = fields.Many2many(
        "shoes.ranking",
        compute="_compute_shoes_assortment_ranking_ids",
    )

    def _compute_shoes_assortment_ranking_ids(self):
        for record in self:
            ranking = self.env["shoes.ranking"].search([('product_tmpl_id','=', record.product_tmpl_single_id.id)])
            record.shoes_assortment_ranking_ids = [(6,0,ranking.ids)]
