# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json
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
            ('salesman_country', 'Salesman and country'),
            ('manufacturer_sales', 'Sales by manufacturer'),
            ('sales_country', 'Sales by country'),
            ('sales_country_graphic', 'Graphic sales by country'),
            ('sale_type', 'Sales type'),
            ('sale_last', 'Sales by last'),
            ('stadistic_sales', 'Graphic stadistic Sales'),
            ('salesman_model', 'Salesman model'),
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

    """ quito para poner m2m2:
    shoes_campaign2_id = fields.Many2one(
        comodel_name='project.project',
        string='Compare to',
        domain=[('is_shoes_campaign', '=', True)]
    )
    """

    line_ids = fields.One2many(
        comodel_name='shoes.analysis.line',
        inverse_name='shoes_analysis_id',
        string='Lines'
    )

    total = fields.Integer(
        'Total',
        compute='_compute_total',
    )

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
        # Es buena práctica iterar sobre self, ya que un botón puede
        # (aunque sea raro) ser llamado desde una vista de lista
        # seleccionando múltiples registros.
        for record in self:
            # Usamos una cadena de if/elif para encontrar el tipo y
            # llamar al método correspondiente.
            if record.type == 'salesman_sales_delivery':
                record._compute_salesman_sales_delivery()

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

            elif record.type == 'stadistic_sales':
                record._compute_stadistic_sales()

            elif record.type == 'salesman_model':
                record._compute_salesman_model()

            elif record.type == 'customer_comparison':
                record._compute_customer_comparison()

        return True

    # --- Submétodos (Stubs) ---
    import json
    # ... (imports)

    def _compute_salesman_sales_delivery(self):
        """
        Lógica para 'Sales and delivery' (M2M Eficiente).
        Usa el campo 'shoes_campaign_id' almacenado en sale.order.line
        para agrupar en solo dos consultas.
        """
        self.ensure_one()

        all_campaigns = self.shoes_campaign_id | self.shoes_campaign_ids

        if not all_campaigns:
            self.line_ids.unlink()
            return True

        self.line_ids.unlink()

        field_name_for_pairs_on_line = 'pairs_count'

        campaign_name_map = {c.id: c.name for c in all_campaigns}

        # --- CONSULTA 1: Total Vendido ---
        domain_order = [
            ('shoes_campaign_id', 'in', all_campaigns.ids),
            ('state', 'in', ['sale', 'done'])
        ]
        sales_data = self.env['sale.order'].read_group(
            domain=domain_order,
            fields=['user_id', 'amount_total', 'shoes_campaign_id'],
            groupby=['user_id', 'shoes_campaign_id'],
            lazy=False
        )

        # --- CONSULTA 2: Total Pares ---
        domain_line = [
            ('shoes_campaign_id', 'in', all_campaigns.ids),
            ('order_id.state', 'in', ['sale', 'done'])
        ]
        pairs_data = self.env['sale.order.line'].read_group(
            domain=domain_line,
            fields=[
                'salesman_id',
                f'{field_name_for_pairs_on_line}:sum',
                'shoes_campaign_id'
            ],
            groupby=['salesman_id', 'shoes_campaign_id'],
            lazy=False
        )

        # --- 5. Combinar los resultados en un mapa ---
        data_map = {}

        # Procesar Ventas
        for group in sales_data:
            user_tuple = group['user_id']
            campaign_tuple = group['shoes_campaign_id']
            if not user_tuple or not campaign_tuple: continue
            user_id, user_name = user_tuple
            campaign_id = campaign_tuple[0]
            if user_id not in data_map:
                data_map[user_id] = {'representante': user_name, 'campanias_data': {}}
            if campaign_id not in data_map[user_id]['campanias_data']:
                data_map[user_id]['campanias_data'][campaign_id] = {'total_vendido': 0, 'pairs_count': 0}
            data_map[user_id]['campanias_data'][campaign_id]['total_vendido'] = group['amount_total']

        # Procesar Pares
        for group in pairs_data:
            user_tuple = group['salesman_id']
            campaign_tuple = group['shoes_campaign_id']
            if not user_tuple or not campaign_tuple: continue
            user_id, user_name = user_tuple
            campaign_id = campaign_tuple[0]
            if user_id not in data_map:
                data_map[user_id] = {'representante': user_name, 'campanias_data': {}}
            if campaign_id not in data_map[user_id]['campanias_data']:
                data_map[user_id]['campanias_data'][campaign_id] = {'total_vendido': 0, 'pairs_count': 0}
            data_map[user_id]['campanias_data'][campaign_id]['pairs_count'] = group[field_name_for_pairs_on_line]

        # --- 6. Crear las líneas de análisis (¡CAMBIO AQUÍ!) ---
        lines_to_create = []

        # Obtenemos el ID de la campaña base
        base_camp_id = self.shoes_campaign_id.id

        for user_data in data_map.values():

            # --- ¡NUEVA VALIDACIÓN! ---
            # Si la campaña base (Actual) no está en los datos de este vendedor,
            # saltamos y no creamos la línea para él.
            if base_camp_id not in user_data['campanias_data']:
                continue

                # (El resto del código es el mismo)
            final_json_data = {
                'representante': user_data['representante'],
                'campanias': []
            }

            for camp_id, totals in user_data['campanias_data'].items():
                final_json_data['campanias'].append({
                    'campania_id': camp_id,
                    'campania_nombre': campaign_name_map.get(camp_id, "N/A"),
                    'total_vendido': totals['total_vendido'],
                    'pairs_count': totals['pairs_count']
                })

            data_json = json.dumps(final_json_data, indent=2, default=str)
            lines_to_create.append((0, 0, {'data': data_json}))

        if lines_to_create:
            self.write({'line_ids': lines_to_create})

        return True


    # CONCATENAR TODAS LAS LINE_IDS EN UN ÚNICO CAMPO HTML:
    analysis_html = fields.Html(
        string="Vista HTML del Análisis",
        compute="_compute_analysis_html",
        store=False # No es necesario guardarlo, se calcula al vuelo
    )

    @api.depends('line_ids.data_html')
    def _compute_analysis_html(self):
        """
        Concatena el HTML de todas las líneas en un solo bloque.
        """
        for record in self:
            # Ordenar las líneas (opcional, pero recomendado)
            # Aquí asumo que quieres ordenar por nombre de representante
            # Puedes cambiar 'representante' por 'id' o lo que veas
            try:
                # Cargar el JSON de cada línea para ordenar
                lines_sorted = sorted(
                    record.line_ids,
                    key=lambda line: json.loads(line.data or '{}').get('representante', '')
                )
            except Exception:
                lines_sorted = record.line_ids # Fallback si el JSON falla

            # Unir el HTML de cada línea
            html_parts = [line.data_html for line in lines_sorted if line.data_html]
            record.analysis_html = "".join(html_parts)





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

    def _compute_stadistic_sales(self):
        """ Lógica para 'Graphic stadistic Sales' """
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