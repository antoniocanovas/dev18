# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

class ShoesAnalysis(models.Model):
    _name = 'shoes.analysis'
    _description = 'Shoes Analysis'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True
    )

    type = fields.Selection(
        selection=[
            ('salesman_sales_delivery', 'Sales and delivery'),
            ('product_ranking', 'Product Ranking'),
            ('last_ranking', 'Last Ranking'),
            ('campaign_product_ranking', 'Campaign product ranking'),
            ('campaign_last_ranking', 'Campaign last ranking'),
            ('salesman_model', 'Salesman model'),
            ('salesman_country', 'Salesman and country'),
            ('manufacturer_sales', 'Sales by manufacturer'),
            ('sales_country', 'Sales by country'),
            ('sales_country_graphic', 'Graphic sales by country'),
            ('sale_type', 'Sales type'),
            ('sale_last', 'Sales by last'),
            ('customer_comparison', 'Customer comparison'),
        ]
    )

    shoes_campaign_id = fields.Many2one(
        comodel_name='project.project',
        string='Campaign',
        domain=[('is_shoes_campaign', '=', True)],
        required=True
    )

    shoes_campaign_ids = fields.Many2many(
        comodel_name='project.project',
        string='Compare to',
        domain=[('is_shoes_campaign', '=', True)],
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer'
    )

    resume_html = fields.Html(
        string='Resume',
        store=True,
        readonly=True,
    )

    analysis_html = fields.Html(
        string="Vista HTML del Análisis",
        store=True,
        readonly=True,
    )

    ranking_line_ids = fields.Many2many(
        comodel_name='shoes.ranking',
        string="Ranking Lines",
        compute='_compute_ranking_line_ids',
        readonly=True,
        store=False,
    )

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    @api.depends('shoes_campaign_id', 'type')
    def _compute_ranking_line_ids(self):
        for analysis in self:
            ranking_types = ['product_ranking', 'campaign_product_ranking', 'last_ranking', 'campaign_last_ranking']
            if analysis.type in ranking_types:
                domain = [('shoes_campaign_id', '=', analysis.shoes_campaign_id.id)]
                if analysis.type in ['product_ranking', 'campaign_product_ranking']:
                    domain.append(('product_tmpl_id', '!=', False))
                elif analysis.type in ['last_ranking', 'campaign_last_ranking']:
                    domain.append(('shoes_last_id', '!=', False))
                analysis.ranking_line_ids = self.env['shoes.ranking'].search(domain)
            else:
                analysis.ranking_line_ids = False

    def update_shoes_analysis(self):
        """
        Actualiza los datos del análisis.
        Centraliza el cálculo de rankings y luego llama al método específico
        de cada informe.
        """
        for record in self:
            # 1. Centralización del cálculo de rankings
            if record.type != 'salesman_sales_delivery':
                campaigns_to_update = record.shoes_campaign_id | record.shoes_campaign_ids
                for campaign in campaigns_to_update:
                    self.env['shoes.ranking']._update_ranking_for_campaign(campaign)

            # 2. Despachador (Dispatcher) para la generación de informes
            if record.type == 'salesman_sales_delivery':
                record._compute_salesman_sales_delivery()
            elif record.type == 'campaign_product_ranking':
                record._compute_campaign_product_ranking()
            elif record.type == 'product_ranking':
                record._compute_product_sales_ranking()
            elif record.type == 'last_ranking':
                record._compute_last_ranking()
            elif record.type == 'campaign_last_ranking':
                record._compute_campaign_last_ranking()
            elif record.type == 'salesman_model':
                record._compute_salesman_model()
            elif record.type == 'salesman_country':
                record._compute_salesman_country()
            elif record.type == 'manufacturer_sales':
                record._compute_manufacturer_sales()
            elif record.type == 'sales_country':
                record._compute_sales_country()
            elif record.type == 'sales_country_graphic':
                record._compute_sales_country_graphic()
            elif record.type == 'sale_type':
                record._compute_sale_type()
            elif record.type == 'sale_last':
                record._compute_sale_last()
            elif record.type == 'customer_comparison':
                record._compute_customer_comparison()

        return True

    def _compute_salesman_country(self):
        self.ensure_one()
        return True
    def _compute_manufacturer_sales(self):
        self.ensure_one()
        return True
    def _compute_sales_country(self):
        self.ensure_one()
        return True
    def _compute_sales_country_graphic(self):
        self.ensure_one()
        return True
    def _compute_sale_type(self):
        self.ensure_one()
        return True
    def _compute_sale_last(self):
        self.ensure_one()
        return True
    def _compute_customer_comparison(self):
        self.ensure_one()
        return True

    @api.constrains('shoes_campaign_id')
    def _check_shoes_campaign_id(self):
        for record in self:
            if record.type == 'product_ranking':
                exist = self.env['shoes.analysis'].search([
                    ('shoes_campaign_id', '=', record.shoes_campaign_id.id),
                    ('id', '!=', record.id),
                    ('type', 'in', ['product_ranking']),
                ])
                if exist:
                    raise UserError('Ya existe un informe para esta campaña')