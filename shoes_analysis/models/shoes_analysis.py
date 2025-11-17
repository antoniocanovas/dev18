# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import html_escape
from odoo.tools.misc import formatLang

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
            ('customer_comparison', 'Customer comparison'),
            ('salesman_country', 'Por representante y país'),
            ('manufacturer_sales', 'Ventas por proveedor'),
            ('sales_by_country', 'Ventas por países'),
            ('sales_by_shipping_mark', 'Ventas por timbrado'),
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

    data = fields.Json(
        string="Structured Data"
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
        for record in self:
            if record.type not in ['salesman_sales_delivery', 'salesman_country', 'manufacturer_sales', 'sales_by_country', 'sales_by_shipping_mark']:
                campaigns_to_update = record.shoes_campaign_id | record.shoes_campaign_ids
                for campaign in campaigns_to_update:
                    self.env['shoes.ranking']._update_ranking_for_campaign(campaign)

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
            elif record.type == 'customer_comparison':
                record._compute_customer_comparison()
            elif record.type == 'salesman_country':
                record._compute_salesman_country()
            elif record.type == 'manufacturer_sales':
                record._compute_manufacturer_sales()
            elif record.type == 'sales_by_country':
                record._compute_sales_by_country()
            elif record.type == 'sales_by_shipping_mark':
                record._compute_sales_by_shipping_mark()
        return True

    def _generate_resume_html(self, campaign_totals, base_camp_id, comparison_campaigns):
        style_camp, style_net, style_rev, style_avg = "min-width: 150px;", "width: 130px;", "width: 150px;", "width: 130px;"
        html_parts = ['<div style="font-size: 1.1em; font-weight: 600; border-bottom: 2px solid #eee; margin-top: 16px; padding-bottom: 4px; margin-bottom: 8px;">Resumen General de Campañas</div>', '<table class="table table-sm o_main_table" style="width: 100%; table-layout: fixed;">', f'<thead><tr style="font-size: 0.85em; color: #555;"><th style="{style_camp}">Campaña</th><th class="text-end" style="{style_net}">Pares Netos</th><th class="text-end" style="{style_rev}">Facturación Prevista</th><th class="text-end" style="{style_avg}">Precio Medio</th></tr></thead><tbody>']
        def create_row(camp_id, is_base=False):
            data = campaign_totals.get(camp_id)
            if not data: return ""
            netos, fact_prevista = data['netos'], data['fact_prevista']
            avg_price = (fact_prevista / netos) if netos > 0 else 0.0
            tag, label = ("b", " (Actual)") if is_base else ("span", " (Objetivo)")
            return (f'<tr><td><{tag}>{html_escape(data["nombre"])}{label}</{tag}></td>'
                    f'<td class="text-end"><{tag}>{netos} Pairs</{tag}></td>'
                    f'<td class="text-end"><{tag}>{fact_prevista:.2f} €</{tag}></td>'
                    f'<td class="text-end"><{tag}>{avg_price:.2f} €</{tag}></td></tr>')
        if base_camp_id: html_parts.append(create_row(base_camp_id, is_base=True))
        for obj_camp in comparison_campaigns:
            if obj_camp.id != base_camp_id: html_parts.append(create_row(obj_camp.id))
        html_parts.append('</tbody></table>')
        return "".join(html_parts)

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