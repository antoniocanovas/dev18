from odoo import models
from odoo.tools import html_escape
from collections import defaultdict
from odoo.tools.misc import formatLang

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def _get_objective_perc_html(self, current, objective, style_str):
        if objective == 0:
            return f'<td class="text-end" style="{style_str} color: green;"><b>+&infin;%</b></td>' if current > 0 else f'<td class="text-end" style="{style_str}">-</td>'
        perc = current / objective
        color = 'green' if perc >= 1.0 else 'red'
        return f'<td class="text-end" style="{style_str} color: {color};"><b>{perc:.1%}</b></td>'

    def _compute_sales_by_shipping_mark(self):
        """
        Genera el informe HTML y los datos JSON para las ventas agrupadas por timbrado.
        """
        self.ensure_one()
        analysis = self
        
        all_campaigns = analysis.shoes_campaign_id | analysis.shoes_campaign_ids
        if not all_campaigns:
            analysis.write({'analysis_html': "<p>No hay campañas seleccionadas.</p>", 'resume_html': False, 'data': False})
            return True

        # 1. Lógica de cálculo
        domain = [
            ('order_id.shoes_campaign_id', 'in', all_campaigns.ids),
            ('order_id.state', 'in', ['sale', 'done']),
            ('sale_type_id', '!=', False),
            '|',
                '&', ('product_id.is_pair', '=', True), ('product_id.product_tmpl_id', '!=', False),
                '&', ('product_id.is_assortment', '=', True), ('product_id.product_tmpl_single_id', '!=', False),
        ]

        sales_data = self.env['sale.order.line'].read_group(
            domain,
            fields=['price_subtotal', 'product_uom_qty', 'pairs_count', 'shoes_pair_cancelled_qty'],
            groupby=['sale_type_id', 'shoes_campaign_id'],
            lazy=False
        )

        # 2. Estructurar datos
        data_map = defaultdict(lambda: defaultdict(lambda: {'net_pairs': 0, 'net_sales': 0}))
        all_type_ids = set()
        campaign_totals = defaultdict(lambda: {'netos': 0, 'fact_prevista': 0.0})

        for group in sales_data:
            type_id = group['sale_type_id'][0]
            campaign_id = group['shoes_campaign_id'][0]
            all_type_ids.add(type_id)
            
            net_pairs = (group['product_uom_qty'] * group.get('pairs_count', 1)) - group.get('shoes_pair_cancelled_qty', 0)
            net_sales = group['price_subtotal']

            data_map[type_id][campaign_id]['net_pairs'] += net_pairs
            data_map[type_id][campaign_id]['net_sales'] += net_sales

            campaign_totals[campaign_id]['netos'] += net_pairs
            campaign_totals[campaign_id]['fact_prevista'] += net_sales
            campaign_totals[campaign_id]['nombre'] = self.env['project.project'].browse(campaign_id).name

        # 3. Generar HTML y JSON
        html_parts, json_output = [], []
        shipping_marks = self.env['sale.order.type'].browse(list(all_type_ids)).sorted('name')
        
        for mark in shipping_marks:
            mark_html = [f"<div style='border: 2px solid #333; border-radius: 5px; margin-bottom: 30px; padding: 20px; background-color: #f0f0f0; page-break-inside: avoid;'>"]
            mark_html.append(f"<h2 style='font-size: 2em; font-weight: bold; margin-bottom: 20px;'>{html_escape(mark.name)}</h2>")
            mark_json = {'shipping_mark_id': mark.id, 'shipping_mark_name': mark.name, 'campaigns': []}

            campaigns_data = data_map[mark.id]
            
            style_th = "padding: 8px; border-bottom: 2px solid #333;"
            mark_html.append(f"<table class='table table-sm' style='font-size: 0.9em;'><thead><tr><th class='text-start' style='{style_th}'>Campaña</th><th class='text-end' style='{style_th}'>Pares Netos</th><th class='text-end' style='{style_th}'>Ventas Netas</th><th class='text-end' style='{style_th}'>% Obj. Pares</th><th class='text-end' style='{style_th}'>% Obj. Ventas</th></tr></thead><tbody>")
            
            base_camp_stats = campaigns_data.get(analysis.shoes_campaign_id.id, {'net_pairs': 0, 'net_sales': 0})

            for camp_id, stats in campaigns_data.items():
                camp = self.env['project.project'].browse(camp_id)
                is_main = (camp_id == analysis.shoes_campaign_id.id)
                tag = "b" if is_main else "span"
                
                row_html = f"<tr><td class='text-start'><{tag}>{html_escape(camp.name)}</{tag}></td>"
                row_html += f"<td class='text-end'><{tag}>{int(stats['net_pairs'])}</{tag}></td>"
                row_html += f"<td class='text-end'><{tag}>{formatLang(self.env, stats['net_sales'], currency_obj=analysis.currency_id)}</{tag}></td>"
                
                if is_main:
                    row_html += "<td class='text-end'>-</td><td class='text-end'>-</td>"
                else:
                    row_html += self._get_objective_perc_html(base_camp_stats['net_pairs'], stats['net_pairs'], "padding: 8px;")
                    row_html += self._get_objective_perc_html(base_camp_stats['net_sales'], stats['net_sales'], "padding: 8px;")
                
                row_html += "</tr>"
                mark_html.append(row_html)
                
                mark_json['campaigns'].append({'campaign_id': camp.id, 'campaign_name': camp.name, 'net_pairs': stats['net_pairs'], 'net_sales': stats['net_sales']})

            mark_html.append("</tbody></table></div>")
            html_parts.extend(mark_html)
            json_output.append(mark_json)

        resume_html = self._generate_resume_html(campaign_totals, analysis.shoes_campaign_id.id, analysis.shoes_campaign_ids)

        analysis.write({
            'analysis_html': "".join(html_parts),
            'resume_html': resume_html,
            'data': json_output
        })
        return True
