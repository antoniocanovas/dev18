# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools import html_escape
from odoo.tools.misc import formatLang

class ShoesAnalysis(models.Model):
    """
    Modelo central para la configuración y visualización de informes de análisis de ventas.
    Cada registro representa un informe específico con su propia configuración y resultado.
    """
    _name = 'shoes.analysis'
    _description = 'Shoes Analysis'
    _order = 'name'

    name = fields.Char(
        string='Name',
        required=True
    )

    type = fields.Selection(
        selection=[
            ('salesman_sales_delivery', 'Ventas y Entregas por Agente'),
            ('salesman_country', 'Ventas por Representante y País'),
            ('manufacturer_sales', 'Ventas por Proveedor'),
            ('sales_by_country', 'Ventas por Países'),
            ('sales_by_shipping_mark', 'Ventas por Timbrado'),
            ('customer_comparison', 'Ventas a cliente por campañas'),
            ('salesman_customers', 'Clientes por representante'),
            ('product_ranking', 'Ranking de Productos (Comparativo)'),
            ('last_ranking', 'Ranking de Hormas (Comparativo)'),
            ('campaign_product_ranking', 'Ranking de productos por campaña con colores'),
            ('campaign_last_ranking', 'Ranking de hormas por campaña con modelos y colores'),
            ('salesman_model', 'Ventas de representante por modelo'),
            ('campaign_manufacturer', 'Campaña por fabricante(s)'),
            ('stock_available', 'Stock disponible')
        ],
        string="Tipo de Informe"
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

    manufacturer_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Manufacturers'
    )

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Customer'
    )

    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Pricelist'
    )

    referrer_id = fields.Many2one(
        comodel_name='res.users',
        string='Referrer'
    )

    # Campo utilizado para consolidación de datos en algunos informes:
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

    public = fields.Boolean(
        string='Public Report',
        default=False,
        help='If checked, this report will be visible to all sales users, '
             'even if they are not the referrer.'
    )

    @api.depends('shoes_campaign_id', 'type', 'manufacturer_ids')
    def _compute_ranking_line_ids(self):
        """
        Calcula las líneas de ranking a mostrar en la vista de análisis.
        """
        for analysis in self:
            analysis.ranking_line_ids = False
            domain = [('shoes_campaign_id', '=', analysis.shoes_campaign_id.id)]
            if analysis.manufacturer_ids:
                domain.append(('manufacturer_id', 'in', analysis.manufacturer_ids.ids))

            if analysis.type in ('product_ranking', 'campaign_product_ranking', 'campaign_manufacturer'):
                domain.append(('product_tmpl_id', '!=', False))
                analysis.ranking_line_ids = self.env['shoes.ranking'].search(domain)
            elif analysis.type in ('last_ranking', 'campaign_last_ranking'):
                domain.append(('shoes_last_id', '!=', False))
                analysis.ranking_line_ids = self.env['shoes.ranking'].search(domain)

    def update_shoes_analysis(self):
        """
        Punto de entrada principal para generar/actualizar el análisis.
        """
        for record in self:
            if record.type not in [
                'salesman_sales_delivery', 'salesman_country', 'manufacturer_sales',
                'sales_by_country', 'sales_by_shipping_mark', 'customer_comparison', 'salesman_customers',
                'stock_available'
            ]:
                campaigns_to_update = record.shoes_campaign_id | record.shoes_campaign_ids
                self.env['shoes.ranking']._update_ranking_for_campaign(campaigns_to_update)

            method_name = f'_compute_{record.type}'
            if hasattr(record, method_name):
                getattr(record, method_name)()
        return True

    def action_print_report(self):
        """
        Genera el informe PDF del análisis actual.
        """
        self.ensure_one()
        if not self.data:
            raise UserError("Nada que imprimir.")
        return self.env.ref('shoes_analysis.action_report_shoes_analysis').report_action(self)

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
                    f'<td class="text-end"><{tag}>{formatLang(self.env, fact_prevista, currency_obj=self.currency_id)}</{tag}></td>'
                    f'<td class="text-end"><{tag}>{formatLang(self.env, avg_price, currency_obj=self.currency_id)}</{tag}></td></tr>')
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