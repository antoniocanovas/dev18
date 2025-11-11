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


    # --- MÉTODO COMPUTE HTML ---
    # --- El método helper _get_objective_perc_html
    # --- (el de antes) sigue aquí sin cambios...
    def _get_objective_perc_html(self, current, objective):
        if objective == 0:
            if current > 0:
                return '<td class="text-end" style="color: green;"><b>+&infin;%</b></td>'
            else:
                return '<td class="text-end">-</td>'
        perc = current / objective
        formatted_perc = f"{perc:.1%}"
        if perc >= 1.0:
            return f'<td class="text-end" style="color: green;"><b>{formatted_perc}</b></td>'
        else:
            return f'<td class="text-end" style="color: red;"><b>{formatted_perc}</b></td>'

            # --- MÉTODO COMPUTE HTML ACTUALIZADO ---
    @api.depends('data', 'shoes_analysis_id.shoes_campaign_id')
    def _compute_data_html(self):

        for line in self:
            # ... (Toda la lógica inicial de carga de datos es igual) ...
            if not line.data:
                line.data_html = False
                continue

            base_camp_id = line.shoes_analysis_id.shoes_campaign_id.id
            if not base_camp_id:
                line.data_html = "<p>Error: No hay Campaña Principal definida.</p>"
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

            # --- 3. Construir HTML (¡CAMBIOS AQUÍ!) ---
            salesman_name_safe = html_escape(data_dict.get('representante', ''))

            # --- Encabezado de sección para el Comercial ---
            html_parts = [
                f'<div style="font-size: 1.1em; font-weight: 600; border-bottom: 2px solid #eee; margin-top: 16px; padding-bottom: 4px; margin-bottom: 8px;">'
                f'{salesman_name_safe}'
                f'</div>'
            ]

            # --- Tabla sin cabecera ---
            html_parts.append(
                '<table class="table table-sm o_main_table" style="width: 100%;">'
                '<tbody>'
            )

            # --- 4. Renderizar Fila Base (Actual) ---
            base_camp_name_safe = html_escape(base_data.get('campania_nombre', 'N/A'))
            html_parts.append(
                f"<tr>"
                # --- Sin 'Comercial' <td> ---
                f'<td style="min-width: 150px;"><b>{base_camp_name_safe} (Actual)</b></td>'
                # --- "Pairs" añadido ---
                f'<td class="text-end"><b>{base_pairs} Pairs</b></td>'
                f'<td class="text-end"><b>{base_sales:.2f} €</b></td>'
                f'<td class="text-end" style="width: 90px;">-</td>'
                f'<td class="text-end" style="width: 90px;">-</td>'
                f"</tr>"
            )

            # --- 5. Renderizar Filas de Comparación (Objetivos) ---
            for camp_data in compare_data_list:
                camp_name_safe = html_escape(camp_data.get('campania_nombre', 'N/A'))
                objective_pairs = camp_data.get('pairs_count', 0)
                objective_sales = camp_data.get('total_vendido', 0.0)

                perc_pairs_html = self._get_objective_perc_html(base_pairs, objective_pairs)
                perc_sales_html = self._get_objective_perc_html(base_sales, objective_sales)

                html_parts.append(
                    f"<tr>"
                    f"<td>{camp_name_safe} (Objetivo)</td>"
                    # --- "Pairs" añadido ---
                    f'<td class="text-end">{objective_pairs} Pairs</td>'
                    f'<td class="text-end">{objective_sales:.2f} €</td>'
                    f"{perc_pairs_html}"
                    f"{perc_sales_html}"
                    f"</tr>"
                )

            html_parts.append('</tbody></table>')
            line.data_html = "".join(html_parts)