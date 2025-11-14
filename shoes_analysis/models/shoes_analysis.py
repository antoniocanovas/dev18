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
            ('stadistic_sales', 'Graphic stadistic Sales'),
            ('salesman_country', 'Salesman and country'),
            ('manufacturer_sales', 'Sales by manufacturer'),
            ('sales_country', 'Sales by country'),
            ('sales_country_graphic', 'Graphic sales by country'),
            ('sale_type', 'Sales type'),
            ('sale_last', 'Sales by last'),
            ('salesman_model', 'Salesman model'),
            ('customer_comparison', 'Customer comparison'),
            ('product_ranking', 'Product Ranking'),
            ('last_ranking', 'Last Ranking'),
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

    line_ids = fields.One2many(
        comodel_name='shoes.analysis.line',
        inverse_name='shoes_analysis_id',
        string='Lines'
    )

    total = fields.Integer(
        'Total',
        compute='_compute_total',
    )

    # Campo html para resumen de resultados en líneas:
    resume_html = fields.Html(
        string='Resume',
        store=True,
        readonly=True,
    )

    # CONCATENAR TODAS LAS LINE_IDS EN UN ÚNICO CAMPO HTML:
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
        store=False, # No se almacena en la base de datos
    )

    currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id
    )

    @api.depends('shoes_campaign_id', 'type')
    def _compute_ranking_line_ids(self):
        for analysis in self:
            domain = [('shoes_campaign_id', '=', analysis.shoes_campaign_id.id)]
            if analysis.type == 'product_ranking':
                domain.append(('product_tmpl_id', '!=', False))
            elif analysis.type == 'last_ranking':
                domain.append(('shoes_last_id', '!=', False))
            else:
                analysis.ranking_line_ids = False
                continue

            analysis.ranking_line_ids = self.env['shoes.ranking'].search(domain)


    @api.depends('line_ids.data_html')
    def _compute_and_set_analysis_html(self):
        """
        Calcula y GUARDA el HTML de análisis (antiguo _compute_analysis_html)
        """
        self.ensure_one()

        try:
            lines_sorted = sorted(
                self.line_ids,
                key=lambda line: json.loads(line.data or '{}').get('representante', '')
            )
        except Exception:
            lines_sorted = self.line_ids

        html_parts = [line.data_html for line in lines_sorted if line.data_html]
        self.write({'analysis_html': "".join(html_parts)})


    def _compute_total(self):
        for record in self:
            total = 0
            for li in record.line_ids:
                total += li.total
            record.total = total

    # --- Método Principal (Dispatcher) ---

    def update_shoes_analysis(self):
        """
        Actualiza los datos del análisis.
        Este método actúa como un despachador (dispatcher) que llama al
        submétodo apropiado basado en el campo 'type' del registro.
        """
        for record in self:
            if record.type == 'salesman_sales_delivery':
                record._compute_salesman_sales_delivery()
            elif record.type == 'stadistic_sales':
                record._compute_stadistic_sales()
            elif record.type == 'product_ranking':
                record._compute_product_sales_ranking()
            elif record.type == 'last_ranking':
                record._compute_last_ranking()
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
            elif record.type == 'salesman_model':
                record._compute_salesman_model()
            elif record.type == 'customer_comparison':
                record._compute_customer_comparison()

        return True


    def _compute_salesman_country(self):
        """ Lógica para 'Salesman and country' """
        self.ensure_one()
        # TODO: Añadir lógica de cálculo aquí
        return True

    def _compute_manufacturer_sales(self):
        """ Lógica para 'Sales by manufacturer' """
        self.ensure_one()
        # TODO: Añadir lógica de cálculo aquí
        return True

    def _compute_sales_country(self):
        """ Lógica para 'Sales by country' """
        self.ensure_one()
        # TODO: Añadir lógica de cálculo aquí
        return True

    def _compute_sales_country_graphic(self):
        """ Lógica para 'Graphic sales by country' """
        self.ensure_one()
        # TODO: Añadir lógica de cálculo aquí
        return True

    def _compute_sale_type(self):
        """ Lógica para 'Sales type' """
        self.ensure_one()
        # TODO: Añadir lógica de cálculo aquí
        return True

    def _compute_sale_last(self):
        """ Lógica para 'Sales by last' """
        self.ensure_one()
        # TODO: Añadir lógica de cálculo aquí
        return True

    def _compute_salesman_model(self):
        """ Lógica para 'Salesman model' """
        self.ensure_one()
        # TODO: Añadir lógica de cálculo aquí
        return True

    def _compute_customer_comparison(self):
        """ Lógica para 'Customer comparison' """
        self.ensure_one()
        # TODO: Añadir lógica de cálculo aquí
        return True

    @api.constrains('shoes_campaign_id')
    def _check_shoes_campaign_id(self):
        for record in self:
            exist = self.env['shoes.analysis'].search(
                [
                    ('shoes_campaign_id', '=', record.shoes_campaign_id.id),
                    ('id','!=',record.id),
                    ('type','in',['product_ranking']),
                ]
            )
            if exist.ids and record.type == 'product_ranking':
                raise UserError('Ya existe un informe para esta campaña')