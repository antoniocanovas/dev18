from odoo import models, api
from odoo.tools.misc import formatLang

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    # -----------------------------------------------------------------
    # MÉTODO PRINCIPAL (Orquestador)
    # -----------------------------------------------------------------

    def _compute_last_ranking(self):
        """
        Método principal que orquesta la actualización de datos y la
        generación del informe HTML para el ranking de hormas.
        """
        for analysis in self:
            main_campaign = analysis.shoes_campaign_id
            comparison_campaigns = analysis.shoes_campaign_ids
            all_campaigns = main_campaign | comparison_campaigns

            # 1. Asegura que los datos de TODAS las campañas están actualizados
            #    (Esto actualiza tanto productos como hormas)
            for campaign in all_campaigns:
                self.env['shoes.ranking']._update_ranking_for_campaign(campaign)

            # 2. Busca todas las líneas de HORMAS de todas las campañas involucradas
            all_ranking_lines = self.env['shoes.ranking'].search([
                ('shoes_campaign_id', 'in', all_campaigns.ids),
                ('shoes_last_id', '!=', False)
            ])

            # 3. Ordena el conjunto completo por el neto de pares
            sorted_lines = all_ranking_lines.sorted(key=lambda r: r.pairs_count_net, reverse=True)

            # 4. Genera el HTML con la lista consolidada y ordenada
            analysis._generate_last_ranking_html(sorted_lines)

        return True

    # -----------------------------------------------------------------
    # MÉTODO 2: CREACIÓN DE HTML (analysis_html)
    # -----------------------------------------------------------------

    def _generate_last_ranking_html(self, ranking_lines):
        """
        Genera el informe HTML para el ranking de hormas.
        """
        self.ensure_one()
        analysis = self

        if not ranking_lines:
            analysis.analysis_html = "<p>No hay datos de ranking para mostrar.</p>"
            return

        # 1. Crear mapa de colores para las campañas de comparación
        comparison_campaigns = analysis.shoes_campaign_ids
        colors = ['#4CAF50', '#2196F3', '#FFC107', '#E91E63', '#9C27B0', '#FF5722']
        campaign_color_map = {}
        for i, campaign in enumerate(comparison_campaigns):
            campaign_color_map[campaign.id] = colors[i % len(colors)]

        html_lines = []

        # Estilos CSS
        style_table = "width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 14px;"
        style_th = "border-bottom: 2px solid #dee2e6; padding: 10px 8px; text-align: left; font-weight: 600;"
        style_td = "border-bottom: 1px solid #dee2e6; padding: 10px 8px; vertical-align: middle;"
        style_td_num = f"{style_td} text-align: right;"

        # 2. El Header (Cabecera)
        html_lines.append(f"<table style='{style_table}'>")
        html_lines.append("<thead><tr>")
        html_lines.append(f"<th style='{style_th} width: 60px;'>Ranking</th>")
        html_lines.append(f"<th style='{style_th}'>Horma</th>")
        html_lines.append(f"<th style='{style_th} text-align: right;'>Total Vend.</th>")
        html_lines.append(f"<th style='{style_th} text-align: right;'>Total Canc.</th>")
        html_lines.append(f"<th style='{style_th} text-align: right;'>Netos</th>")
        html_lines.append(f"<th style='{style_th} text-align: right;'>Importe Neto</th>")
        html_lines.append("</tr></thead>")

        # 3. El Body (Líneas)
        html_lines.append("<tbody>")

        total_sale = 0.0
        total_cancel = 0.0
        total_net = 0.0
        total_amount = 0.0

        for line in ranking_lines:
            is_main_campaign = (line.shoes_campaign_id.id == analysis.shoes_campaign_id.id)
            font_weight_style = "bold" if is_main_campaign else "normal"
            
            row_style = ""
            if not is_main_campaign:
                color = campaign_color_map.get(line.shoes_campaign_id.id, '#ccc')
                row_style = f"style='border-left: 5px solid {color};'"
            
            campaign_tag = "" if is_main_campaign else f"<br/><span style='color: #888; font-size: 11px;'>({line.shoes_campaign_id.name})</span>"

            last_name = line.shoes_last_id.name or "N/A"
            last_display = f"<strong>{last_name}</strong>{campaign_tag}"

            formatted_amount = formatLang(
                analysis.env,
                line.sale_net_amount,
                currency_obj=line.currency_id
            )

            html_lines.append(f"<tr {row_style}>")
            html_lines.append(f"<td style='{style_td_num} font-size: 1.1em; font-weight: {font_weight_style};'>{line.ranking}</td>")
            html_lines.append(f"<td style='{style_td}'>{last_display}</td>")
            html_lines.append(f"<td style='{style_td_num} font-weight: {font_weight_style};'>{line.pairs_count_sale} Pairs</td>")
            html_lines.append(f"<td style='{style_td_num} font-weight: {font_weight_style};'>{line.pairs_count_cancel} Pairs</td>")
            html_lines.append(f"<td style='{style_td_num} font-weight: {font_weight_style};'>{line.pairs_count_net} Pairs</td>")
            html_lines.append(f"<td style='{style_td_num} font-weight: {font_weight_style};'>{formatted_amount}</td>")
            html_lines.append("</tr>")

            if is_main_campaign:
                total_sale += line.pairs_count_sale
                total_cancel += line.pairs_count_cancel
                total_net += line.pairs_count_net
                total_amount += line.sale_net_amount

        html_lines.append("</tbody>")

        # 4. El Footer (Totales)
        formatted_total_amount = formatLang(
            analysis.env,
            total_amount,
            currency_obj=analysis.currency_id
        )
        style_td_total = f"{style_td_num} font-weight: bold; border-top: 2px solid #dee2e6;"

        html_lines.append("<tfoot>")
        html_lines.append("<tr>")
        html_lines.append(f"<td style='{style_td_total} text-align: left;' colspan='2'>TOTALES (Campaña Principal)</td>")
        html_lines.append(f"<td style='{style_td_total}'>{total_sale} Pairs</td>")
        html_lines.append(f"<td style='{style_td_total}'>{total_cancel} Pairs</td>")
        html_lines.append(f"<td style='{style_td_total}'>{total_net} Pairs</td>")
        html_lines.append(f"<td style='{style_td_total}'>{formatted_total_amount}</td>")
        html_lines.append("</tr>")
        html_lines.append("</tfoot>")
        html_lines.append("</table>")

        # 5. Guardar el HTML completo
        analysis.analysis_html = "\n".join(html_lines)
