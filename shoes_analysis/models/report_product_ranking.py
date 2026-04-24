import json
from odoo import models, fields, api
from odoo.tools import float_is_zero
from odoo.tools.image import image_data_uri
from odoo.tools.misc import formatLang

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def _compute_product_ranking(self):
        """
        Genera el informe HTML para el ranking de productos.
        El cálculo de datos ya se ha hecho de forma centralizada.
        """
        for analysis in self:
            all_campaigns = analysis.shoes_campaign_id | analysis.shoes_campaign_ids
            ranking_lines_domain = [
                ('shoes_campaign_id', 'in', all_campaigns.ids),
                ('product_tmpl_id', '!=', False)
            ]
            all_ranking_lines = self.env['shoes.ranking'].search(ranking_lines_domain)
            sorted_lines = all_ranking_lines.sorted(key=lambda r: r.pairs_count_net, reverse=True)
            
            recalculated_lines = []
            for line in sorted_lines:
                product_template = line.product_tmpl_id
                product_product = product_template.product_variant_id
                
                price = 0.0
                if analysis.pricelist_id:
                    price = analysis.pricelist_id._get_product_price(product_product, quantity=1)
                else:
                    price = product_product.lst_price

                recalculated_line = {
                    'line': line,
                    'price': price,
                    'sale_net_amount': line.pairs_count_net * price,
                }
                recalculated_lines.append(recalculated_line)
            
            analysis._generate_ranking_html(recalculated_lines)
        return True

    def _generate_ranking_html(self, ranking_data):
        """
        Genera el informe HTML y los datos JSON basados en los registros 'shoes.ranking'.
        """
        self.ensure_one()
        analysis = self

        if not ranking_data:
            analysis.write({
                'analysis_html': "<p>No hay datos de ranking para mostrar.</p>",
                'data': False
            })
            return

        # 1. Preparar datos para JSON
        data_for_json = []
        for data in ranking_data:
            line = data['line']
            
            line_data = {
                'name': line.shoes_campaign_id.display_name,
                'ranking': line.ranking,
                'pairs_count_sale': line.pairs_count_sale,
                'pairs_count_cancel': line.pairs_count_cancel,
                'pairs_count_net': line.pairs_count_net,
                'price': data['price'],
                'sale_net_amount': data['sale_net_amount'],
                'currency_id': line.currency_id.id,
                'product_tmpl_id': line.product_tmpl_id.id,
                'shoes_model_material': line.shoes_model_material,
                'shoes_campaign_id': line.shoes_campaign_id.id
            }
            data_for_json.append(line_data)


        # 2. Crear mapa de colores para las campañas de comparación
        comparison_campaigns = analysis.shoes_campaign_ids
        colors = ['#4CAF50', '#2196F3', '#FFC107', '#E91E63', '#9C27B0', '#FF5722']
        campaign_color_map = {c.id: colors[i % len(colors)] for i, c in enumerate(comparison_campaigns)}

        html_lines = []
        style_table = "width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.9em;"
        style_th = "border-bottom: 2px solid #dee2e6; padding: 10px 8px; font-weight: 600;"
        style_td = "border-bottom: 1px solid #dee2e6; padding: 10px 8px; vertical-align: middle;"
        
        html_lines.append(f"<table style='{style_table}'>")
        html_lines.append(f"""
            <thead>
                <tr>
                    <th style='{style_th} text-align: left;'>Ranking</th>
                    <th style='{style_th} text-align: center;'>Imagen</th>
                    <th style='{style_th} text-align: left;'>Producto (Ref.)</th>
                    <th style='{style_th} text-align: right;'>Total Vend.</th>
                    <th style='{style_th} text-align: right;'>Total Canc.</th>
                    <th style='{style_th} text-align: right;'>Netos</th>
                    <th style='{style_th} text-align: right;'>Price</th>
                    <th style='{style_th} text-align: right;'>Importe Neto</th>
                </tr>
            </thead>
        """)
        html_lines.append("<tbody>")

        total_sale, total_cancel, total_net, total_amount = 0.0, 0.0, 0.0, 0.0

        for data in ranking_data:
            line = data['line']
            price = data['price']
            sale_net_amount = data['sale_net_amount']

            is_main_campaign = (line.shoes_campaign_id.id == analysis.shoes_campaign_id.id)
            font_weight_style = "bold" if is_main_campaign else "normal"
            row_style = "page-break-inside: avoid;"
            if not is_main_campaign:
                color = campaign_color_map.get(line.shoes_campaign_id.id, '#ccc')
                row_style += f" border-left: 5px solid {color};"
            
            campaign_tag = "" if is_main_campaign else f"<br/><span style='color: #888; font-size: 11px;'>({line.shoes_campaign_id.display_name})</span>"
            prod_name = line.product_tmpl_id.name or "N/A"
            prod_ref = line.shoes_model_material or ""
            prod_display = f"<strong>{prod_name}</strong><br/><span style='color: #777; font-size: 13px;'>{prod_ref}</span>"
            formatted_price = formatLang(analysis.env, price, currency_obj=analysis.currency_id)
            formatted_amount = formatLang(analysis.env, sale_net_amount, currency_obj=analysis.currency_id)
            
            image_html = ""
            if line.product_tmpl_id and line.product_tmpl_id.image_128:
                image_uri = image_data_uri(line.product_tmpl_id.image_128)
                image_html = f"<div style='text-align: center;'><img src='{image_uri}' style='max-height: 60px; max-width: 60px; object-fit: contain;' alt='Imagen de producto'/></div>"

            html_lines.append(f"<tr style='{row_style}'>")
            html_lines.append(f"<td style='{style_td} text-align: left; font-weight: {font_weight_style};'>{line.shoes_campaign_id.display_name}</td>")
            html_lines.append(f"<td style='{style_td}'>{image_html}</td>")
            html_lines.append(f"<td style='{style_td} text-align: left;'>{prod_display}</td>")
            html_lines.append(f"<td style='{style_td} text-align: right; font-weight: {font_weight_style};'>{line.pairs_count_sale}</td>")
            html_lines.append(f"<td style='{style_td} text-align: right; font-weight: {font_weight_style};'>{line.pairs_count_cancel}</td>")
            html_lines.append(f"<td style='{style_td} text-align: right; font-weight: {font_weight_style};'>{line.pairs_count_net}</td>")
            html_lines.append(f"<td style='{style_td} text-align: right; font-weight: {font_weight_style};'>{formatted_price}</td>")
            html_lines.append(f"<td style='{style_td} text-align: right; font-weight: {font_weight_style};'>{formatted_amount}</td>")
            html_lines.append("</tr>")

            if is_main_campaign:
                total_sale += line.pairs_count_sale
                total_cancel += line.pairs_count_cancel
                total_net += line.pairs_count_net
                total_amount += sale_net_amount

        html_lines.append("</tbody>")
        
        formatted_total_amount = formatLang(analysis.env, total_amount, currency_obj=analysis.currency_id)
        style_td_total = f"border-bottom: 1px solid #dee2e6; padding: 10px 8px; vertical-align: middle; font-weight: bold; border-top: 2px solid #dee2e6;"
        html_lines.append("<tfoot><tr>")
        html_lines.append(f"<td style='{style_td_total} text-align: left;' colspan='3'>TOTALES (Campaña Principal)</td>")
        html_lines.append(f"<td style='{style_td_total} text-align: right;'>{total_sale}</td>")
        html_lines.append(f"<td style='{style_td_total} text-align: right;'>{total_cancel}</td>")
        html_lines.append(f"<td style='{style_td_total} text-align: right;'>{total_net}</td>")
        html_lines.append(f"<td style='{style_td_total}'></td>")
        html_lines.append(f"<td style='{style_td_total} text-align: right;'>{formatted_total_amount}</td>")
        html_lines.append("</tr></tfoot></table>")

        analysis.write({
            'analysis_html': "\n".join(html_lines),
            'data': data_for_json
        })
