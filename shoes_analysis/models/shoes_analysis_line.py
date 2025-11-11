# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json
from odoo.tools import html_escape

class ShoesAnalysisLine(models.Model):
    _name = 'shoes.analysis.line'
    _description = 'Shoes Analysis Line'
    _order = 'id'

    name = fields.Char(
        string='Name',
    )
    
    data = fields.Json(
        string='Data'
    )
    
    data_html = fields.Html(
        string='Data HTML',
        compute="_compute_data_html",
        store=True,
    )
    
    shoes_analysis_id = fields.Many2one(
        comodel_name='shoes.analysis',
        string='Analysis',
        required=True,
        ondelete='cascade'
    )

    shoes_model_material_id = fields.Many2one(
        'shoes.model.material',
        string='Shoes Model Material'
    )

    shoes_task_id = fields.Many2one(
        'project.task',
        string='Model'
    )

    shoes_last_id = fields.Many2one(
        'shoes.last',
        string='Shoes last'
    )

    total = fields.Integer(
        'Total'
    )


    # --- MÉTODO COMPUTE HTML ACTUALIZADO ---
    def _get_objective_perc_html(self, current, objective):
        """
        Helper para calcular el % de objetivo (Actual / Objetivo).
        """
        if objective == 0:
            # Si el objetivo es 0, cualquier venta 'current' es infinita
            if current > 0:
                return '<td class="text-end" style="color: green;"><b>+&infin;%</b></td>'
            # 0 de 0 es indefinido, mostramos '-'
            else:
                return '<td class="text-end">-</td>'

                # --- FÓRMULA CORREGIDA ---
        # (Valor Actual / Valor Objetivo)
        perc = current / objective

        # Formato: 50.0%
        formatted_perc = f"{perc:.1%}"

        # Colorear según el logro
        if perc >= 1.0: # 100% o más (logrado)
            return f'<td class="text-end" style="color: green;"><b>{formatted_perc}</b></td>'
        else: # Menos del 100% (pendiente)
            # Puedes cambiar 'red' por 'orange' si lo prefieres
            return f'<td class="text-end" style="color: red;"><b>{formatted_perc}</b></td>'

    @api.depends('data', 'shoes_analysis_id.shoes_campaign_id')
    def _compute_data_html(self):

        for line in self:
            if not line.data:
                line.data_html = False
                continue

            # Identificar la campaña base (Actual) del análisis padre
            base_camp_id = line.shoes_analysis_id.shoes_campaign_id.id
            if not base_camp_id:
                line.data_html = "<p>Error: No hay Campaña Principal (Actual) definida.</p>"
                continue

            try:
                data_dict = json.loads(line.data)
            except json.JSONDecodeError:
                line.data_html = "<p>Error: JSON mal formado.</p>"
                continue

            # --- 1. Separar la campaña Base de las de Comparación ---
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

            # --- 2. Obtener valores Base (Campaña Actual) ---
            # Estos son el NUMERADOR de nuestra fórmula
            base_pairs = base_data.get('pairs_count', 0)
            base_sales = base_data.get('total_vendido', 0.0)

            # --- 3. Construir HTML ---
            salesman_name_safe = html_escape(data_dict.get('representante', ''))
            num_rows = 1 + len(compare_data_list)

            html_parts = [
                '<table class="table table-sm o_main_table" style="width: 100%;">',
                '<thead><tr>',
                '<th style="min-width: 150px;">Comercial</th>',
                '<th style="min-width: 150px;">Campaña</th>',
                '<th class="text-end">Unidades</th>',
                '<th class="text-end">Ventas</th>',
                '<th class="text-end" style="width: 90px;">% Obj. Pares</th>',
                '<th class="text-end" style="width: 90px;">% Obj. Ventas</th>',
                '</tr></thead>',
                '<tbody>'
            ]

            # --- 4. Renderizar Fila Base (Actual) ---
            base_camp_name_safe = html_escape(base_data.get('campania_nombre', 'N/A'))
            html_parts.append(
                f"<tr>"
                f'<td rowspan="{num_rows}">{salesman_name_safe}</td>'
                f"<td><b>{base_camp_name_safe} (Actual)</b></td>"
                f'<td class="text-end"><b>{base_pairs}</b></td>'
                f'<td class="text-end"><b>{base_sales:.2f} €</b></td>'
                f'<td class="text-end">-</td>'
                f'<td class="text-end">-</td>'
                f"</tr>"
            )

            # --- 5. Renderizar Filas de Comparación (Objetivos) ---
            for camp_data in compare_data_list:
                camp_name_safe = html_escape(camp_data.get('campania_nombre', 'N/A'))

                # Estos son los valores del OBJETIVO (Denominador)
                objective_pairs = camp_data.get('pairs_count', 0)
                objective_sales = camp_data.get('total_vendido', 0.0)

                # Calcular % llamando al helper
                # (Actual / Objetivo)
                perc_pairs_html = self._get_objective_perc_html(base_pairs, objective_pairs)
                perc_sales_html = self._get_objective_perc_html(base_sales, objective_sales)

                html_parts.append(
                    f"<tr>"
                    # Sin <td> para comercial (cubierto por rowspan)
                    f"<td>{camp_name_safe} (Objetivo)</td>"
                    # Mostramos los valores históricos del objetivo
                    f'<td class="text-end">{objective_pairs}</td>'
                    f'<td class="text-end">{objective_sales:.2f} €</td>'
                    # Mostramos el % de consecución
                    f"{perc_pairs_html}"
                    f"{perc_sales_html}"
                    f"</tr>"
                )

            html_parts.append('</tbody></table>')
            line.data_html = "".join(html_parts)