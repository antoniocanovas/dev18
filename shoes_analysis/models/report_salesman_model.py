from odoo import models
from odoo.tools import html_escape
from collections import defaultdict

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def _compute_salesman_model(self):
        """
        Genera un informe de ventas de modelos para un representante, incluyendo
        comparativas con otras campañas.
        """
        self.ensure_one()
        analysis = self

        if not analysis.referrer_id or not analysis.shoes_campaign_id:
            analysis.analysis_html = "<p>Por favor, seleccione una campaña y un representante.</p>"
            return True

        all_campaigns = analysis.shoes_campaign_id | analysis.shoes_campaign_ids

        # 1. Asegura que los datos de TODAS las campañas están actualizados
        self.env['shoes.ranking']._update_ranking_for_campaign(all_campaigns)

        # 2. Obtener el ranking general de productos para TODAS las campañas
        product_ranking_lines = self.env['shoes.ranking'].search([
            ('shoes_campaign_id', 'in', all_campaigns.ids),
            ('product_tmpl_id', '!=', False)
        ])
        product_rank_map = defaultdict(dict)
        for line in product_ranking_lines:
            product_rank_map[line.shoes_campaign_id.id][line.product_tmpl_id.id] = line

        # 3. Obtener datos de ventas para el representante en TODAS las campañas
        domain = [
            ('order_id.shoes_campaign_id', 'in', all_campaigns.ids),
            ('order_id.user_id', '=', analysis.referrer_id.id), # Filtrar por user_id del pedido
            ('order_id.state', 'in', ['sale', 'done']),
            '|',
                '&', ('product_id.is_pair', '=', True), ('product_id.product_tmpl_id', '!=', False),
                '&', ('product_id.is_assortment', '=', True), ('product_id.product_tmpl_single_id', '!=', False),
        ]
        sale_lines = self.env['sale.order.line'].search(domain)

        # 4. Agregar datos por producto y por campaña
        aggregated_data = defaultdict(lambda: defaultdict(lambda: {'pedidos': 0, 'anulados': 0}))
        product_map = {}
        campaign_map = {}

        for line in sale_lines:
            product = line.product_id
            target_template = product.product_tmpl_single_id if product.is_assortment else product.product_tmpl_id
            if not target_template: continue
            
            campaign_id = line.order_id.shoes_campaign_id.id
            if campaign_id not in campaign_map:
                campaign_map[campaign_id] = line.order_id.shoes_campaign_id

            if target_template.id not in product_map:
                product_map[target_template.id] = target_template
            
            line_pairs_gross = line.product_uom_qty * line.pairs_count
            line_pairs_cancelled = line.shoes_pair_cancelled_qty
            
            aggregated_data[campaign_id][target_template.id]['pedidos'] += line_pairs_gross
            aggregated_data[campaign_id][target_template.id]['anulados'] += line_pairs_cancelled

        # 5. Procesar y crear una lista plana para ordenar
        processed_list = []
        for campaign_id, products_data in aggregated_data.items():
            for tmpl_id, data in products_data.items():
                venta_neta = data['pedidos'] + data['anulados']
                if venta_neta > 0:
                    ranking_line = product_rank_map.get(campaign_id, {}).get(tmpl_id)
                    processed_list.append({
                        'referrer_id': analysis.referrer_id.id,
                        'referrer_name': analysis.referrer_id.name,
                        'campaign_id': campaign_id,
                        'campaign_name': campaign_map[campaign_id].display_name,
                        'product_id': product_map[tmpl_id].id,
                        'shoes_model_material': product_map[tmpl_id].shoes_model_material,
                        'product_name': product_map[tmpl_id].name,
                        'pedidos': data['pedidos'],
                        'anulados': data['anulados'],
                        'venta_neta': venta_neta,
                        'ranking_name': ranking_line.name if ranking_line else '',
                        'ranking_value': ranking_line.ranking if ranking_line else 0
                    })
        
        sorted_list = sorted(processed_list, key=lambda x: x['venta_neta'], reverse=True)

        # 6. Generar HTML
        html_parts = []
        
        colors = ['#4CAF50', '#2196F3', '#FFC107', '#E91E63', '#9C27B0', '#FF5722']
        campaign_color_map = {c.id: colors[i % len(colors)] for i, c in enumerate(analysis.shoes_campaign_ids)}

        style_table = "width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 0.9em;"
        style_th = "border-bottom: 2px solid #dee2e6; padding: 10px 8px; text-align: left; font-weight: 600;"
        style_td = "border-bottom: 1px solid #dee2e6; padding: 10px 8px; vertical-align: middle;"
        
        html_parts.append(f"<table style='{style_table}'>")
        html_parts.append(f"""
            <thead>
                <tr>
                    <th style='{style_th}'>Ranking</th>
                    <th style='{style_th} text-align: center;'>Imagen</th>
                    <th style='{style_th}'>Artículo</th>
                    <th style='{style_th}'>Nombre modelo</th>
                    <th style='{style_th} text-align: right;'>Pedidos</th>
                    <th style='{style_th} text-align: right;'>Anulados</th>
                    <th style='{style_th} text-align: right;'>Venta neta</th>
                </tr>
            </thead>
            <tbody>
        """)

        for item in sorted_list:
            product = product_map[item['product_id']]
            is_main_campaign = (item['campaign_id'] == analysis.shoes_campaign_id.id)
            font_weight_style = "bold" if is_main_campaign else "normal"
            
            # Lógica de estilo de fila
            styles = ["page-break-inside: avoid;"]
            if not is_main_campaign:
                color = campaign_color_map.get(item['campaign_id'], '#ccc')
                styles.append(f"border-left: 5px solid {color};")
            
            ranking_value = item.get('ranking_value', 0)
            if 1 <= ranking_value <= 10:
                styles.append("background-color: #E8F5E9;") # Verde claro
            elif 11 <= ranking_value <= 20:
                styles.append("background-color: #FFF9C4;") # Amarillo claro
            
            row_style = f"style='{' '.join(styles)}'" if styles else ""
            
            image_html = ""
            if product.image_256:
                img_base64 = product.image_256.decode('utf-8')
                image_html = f"<div style='text-align: center;'><img src='data:image/png;base64,{img_base64}' style='max-height: 60px; max-width: 60px; object-fit: contain;'/></div>"

            html_parts.append(f"""
                <tr {row_style}>
                    <td style='{style_td} font-weight: {font_weight_style};'>{item['campaign_name']}</td>
                    <td style='{style_td}'>{image_html}</td>
                    <td style='{style_td}'>{product.shoes_model_material or ''}</td>
                    <td style='{style_td}'>{product.name}</td>
                    <td style='{style_td} text-align: right; font-weight: {font_weight_style};'>{int(item['pedidos'])}</td>
                    <td style='{style_td} text-align: right; font-weight: {font_weight_style};'>{int(item['anulados'])}</td>
                    <td style='{style_td} text-align: right; font-weight: {font_weight_style};'>{int(item['venta_neta'])}</td>
                </tr>
            """)

        html_parts.append("</tbody></table>")

        # 7. Escribir en los campos analysis_html y data
        analysis.write({
            'analysis_html': "".join(html_parts),
            'data': sorted_list
        })
        
        return True
