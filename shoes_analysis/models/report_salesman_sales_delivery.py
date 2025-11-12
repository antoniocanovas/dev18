from odoo import fields, models, api
import json
from odoo.tools import html_escape


class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

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



class ShoesAnalysisLine(models.Model):
    _inherit = 'shoes.analysis.line'

    # ... (campos: shoes_analysis_id, data, data_html) ...

    def _get_objective_perc_html(self, current, objective, style_str):
        """
        Helper para calcular el % de objetivo (Actual / Objetivo).
        Ahora acepta un 'style_str' para la alineación.
        """
        # style_str será algo como "width: 90px;"

        if objective == 0:
            if current > 0:
                # El style se combina: "width: 90px; color: green;"
                return f'<td class="text-end" style="{style_str} color: green;"><b>+&infin;%</b></td>'
            else:
                return f'<td class="text-end" style="{style_str}">-</td>'

                # --- FÓRMULA CORREGIDA ---
        perc = current / objective
        formatted_perc = f"{perc:.1%}"

        if perc >= 1.0: # 100% o más (logrado)
            return f'<td class="text-end" style="{style_str} color: green;"><b>{formatted_perc}</b></td>'
        else: # Menos del 100% (pendiente)
            return f'<td class="text-end" style="{style_str} color: red;"><b>{formatted_perc}</b></td>'

    @api.depends('data', 'shoes_analysis_id.shoes_campaign_id')
    def _compute_data_html(self):

        # --- 1. Definir anchos fijos para las columnas ---
        style_camp = "min-width: 150px;" # Dejamos esta flexible
        style_unit = "width: 120px;" # Ancho fijo para "Unidades"
        style_sale = "width: 150px;" # Ancho fijo para "Ventas"
        style_perc = "width: 90px;"  # Ancho fijo para "% Obj."

        for line in self:
            # ... (Lógica de carga de datos sin cambios) ...
            if not line.data:
                line.data_html = False
                continue

            base_camp_id = line.shoes_analysis_id.shoes_campaign_id.id
            if not base_camp_id:
                line.data_html = "<p>Error: No hay Campaña Principal (Actual) definida.</p>"
                continue
            try:
                data_dict = json.loads(line.data)
            except json.JSONDecodeError:
                line.data_html = "<p>Error: JSON mal formado.</p>"
                continue
            all_camp_data = data_dict.get('campanias', [])
            base_data = None
            compare_data_list = []
            for camp_data in all_camp_data:
                if camp_data.get('campania_id') == base_camp_id:
                    base_data = camp_data
                else:
                    compare_data_list.append(camp_data)
            if not base_data:
                line.data_html = "<p>Error: Datos JSON no encontrados para la Campaña Base.</p>"
                continue
            base_pairs = base_data.get('pairs_count', 0)
            base_sales = base_data.get('total_vendido', 0.0)
            # ... (Fin lógica de carga de datos) ...

            # --- 3. Construir HTML (con anchos fijos) ---
            salesman_name_safe = html_escape(data_dict.get('representante', ''))

            html_parts = [
                f'<div style="font-size: 1.1em; font-weight: 600; border-bottom: 2px solid #eee; margin-top: 16px; padding-bottom: 4px; margin-bottom: 8px;">'
                f'{salesman_name_safe}'
                f'</div>'
            ]

            # --- ¡CLAVE! 'table-layout: fixed' fuerza los anchos ---
            html_parts.append(
                '<table class="table table-sm o_main_table" style="width: 100%; table-layout: fixed;">'
                '<tbody>'
            )

            # --- 4. Renderizar Fila Base (Actual) con estilos ---
            base_camp_name_safe = html_escape(base_data.get('campania_nombre', 'N/A'))
            html_parts.append(
                f"<tr>"
                f'<td style="{style_camp}"><b>{base_camp_name_safe} (Actual)</b></td>'
                f'<td class="text-end" style="{style_unit}"><b>{base_pairs} Pairs</b></td>'
                f'<td class="text-end" style="{style_sale}"><b>{base_sales:.2f} €</b></td>'
                f'<td class="text-end" style="{style_perc}">-</td>'
                f'<td class="text-end" style="{style_perc}">-</td>'
                f"</tr>"
            )

            # --- 5. Renderizar Filas de Comparación (Objetivos) con estilos ---
            for camp_data in compare_data_list:
                camp_name_safe = html_escape(camp_data.get('campania_nombre', 'N/A'))
                objective_pairs = camp_data.get('pairs_count', 0)
                objective_sales = camp_data.get('total_vendido', 0.0)

                # Pasamos el string de estilo al helper
                perc_pairs_html = self._get_objective_perc_html(base_pairs, objective_pairs, style_perc)
                perc_sales_html = self._get_objective_perc_html(base_sales, objective_sales, style_perc)

                html_parts.append(
                    f"<tr>"
                    f'<td style="{style_camp}">{camp_name_safe} (Objetivo)</td>'
                    f'<td class="text-end" style="{style_unit}">{objective_pairs} Pairs</td>'
                    f'<td class="text-end" style="{style_sale}">{objective_sales:.2f} €</td>'
                    f"{perc_pairs_html}"
                    f"{perc_sales_html}"
                    f"</tr>"
                )

            html_parts.append('</tbody></table>')
            line.data_html = "".join(html_parts)