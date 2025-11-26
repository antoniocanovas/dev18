from odoo import fields, models, api
import json
from odoo.tools import html_escape
from collections import defaultdict
from odoo.tools.misc import formatLang


class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def _compute_salesman_sales_delivery(self):
        """
        Lógica para 'Sales and delivery'.
        Genera el informe HTML y guarda los datos estructurados en un campo JSON.
        """
        self.ensure_one()
        analysis = self

        all_campaigns = analysis.shoes_campaign_id | analysis.shoes_campaign_ids

        if not all_campaigns:
            analysis.write({
                'analysis_html': "<p>No hay campañas seleccionadas.</p>",
                'resume_html': False,
                'data': False
            })
            return True

        # --- 1. Lógica de cálculo ---
        product_domain_sql = "AND (pt.is_pair = TRUE OR pt.is_assortment = TRUE)"
        company_currency = self.env.company.currency_id
        campaign_name_map = {c.id: c.name for c in all_campaigns}

        # (Consultas SQL y de read_group se mantienen igual)
        query_monetary = """
            SELECT sol.salesman_id, sol.shoes_campaign_id, so.currency_id, so.date_order::date,
                   SUM(sol.price_subtotal) AS total_sales,
                   SUM((sol.product_uom_qty - COALESCE(sol.shoes_pair_cancelled_qty, 0)) * sol.price_unit) AS expected_revenue
            FROM sale_order_line sol JOIN sale_order so ON sol.order_id = so.id
            JOIN product_product pp ON sol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE sol.shoes_campaign_id IN %s AND so.state IN ('sale', 'done') {}
            GROUP BY sol.salesman_id, sol.shoes_campaign_id, so.currency_id, so.date_order::date
        """.format(product_domain_sql)
        self.env.cr.execute(query_monetary, (tuple(all_campaigns.ids),))
        monetary_data = self.env.cr.dictfetchall()
        
        domain_line_sold = [('shoes_campaign_id', 'in', all_campaigns.ids), ('order_id.state', 'in', ['sale', 'done']), '|', ('product_id.product_tmpl_id.is_pair', '=', True), ('product_id.product_tmpl_id.is_assortment', '=', True)]
        pairs_data_sold = self.env['sale.order.line'].read_group(domain_line_sold, ['salesman_id', 'shoes_campaign_id', 'pairs_count:sum', 'shoes_pair_delivered_qty:sum', 'shoes_pair_delivery_pending_qty:sum', 'shoes_pair_cancelled_qty:sum'], ['salesman_id', 'shoes_campaign_id'], lazy=False)
        
        domain_line_cancel = [('shoes_campaign_id', 'in', all_campaigns.ids), ('order_id.state', '=', 'cancel'), '|', ('product_id.product_tmpl_id.is_pair', '=', True), ('product_id.product_tmpl_id.is_assortment', '=', True)]
        pairs_data_cancel = self.env['sale.order.line'].read_group(domain_line_cancel, ['salesman_id', 'shoes_campaign_id', 'pairs_count:sum'], ['salesman_id', 'shoes_campaign_id'], lazy=False)
        
        query_reserved = """
            SELECT sol.salesman_id, sol.shoes_campaign_id, SUM(sm.product_uom_qty) as total_reserved
            FROM stock_move sm JOIN sale_order_line sol ON sm.sale_line_id = sol.id
            JOIN product_product pp ON sol.product_id = pp.id JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE sol.shoes_campaign_id IN %s AND sol.salesman_id IS NOT NULL AND sm.state = 'assigned' {}
            GROUP BY sol.salesman_id, sol.shoes_campaign_id
        """.format(product_domain_sql)
        self.env.cr.execute(query_reserved, (tuple(all_campaigns.ids),))
        reserved_data = self.env.cr.dictfetchall()

        # --- 2. Combinar resultados ---
        data_map = defaultdict(lambda: {'representante': '', 'campanias_data': defaultdict(campaign_template)})
        salesman_ids = set()
        
        def campaign_template(): return {'total_sales': 0.0, 'expected_revenue': 0.0, 'pairs_count': 0, 'pairs_delivered': 0, 'pairs_pending': 0, 'pairs_line_cancelled': 0, 'pairs_order_cancelled': 0, 'pairs_reserved': 0}

        for group in monetary_data:
            user_id, campaign_id = group['salesman_id'], group['shoes_campaign_id']
            if not user_id or not campaign_id: continue
            salesman_ids.add(user_id)
            
            from_currency = self.env['res.currency'].browse(group['currency_id'])
            entry = data_map[user_id]['campanias_data'][campaign_id]
            entry['total_sales'] += from_currency._convert(group['total_sales'] or 0.0, company_currency, self.env.company, group['date_order'])
            entry['expected_revenue'] += from_currency._convert(group['expected_revenue'] or 0.0, company_currency, self.env.company, group['date_order'])
        
        for group in pairs_data_sold:
            if not group['salesman_id'] or not group['shoes_campaign_id']: continue
            user_id, campaign_id = group['salesman_id'][0], group['shoes_campaign_id'][0]
            salesman_ids.add(user_id)
            entry = data_map[user_id]['campanias_data'][campaign_id]
            entry.update({'pairs_count': group['pairs_count'], 'pairs_delivered': group['shoes_pair_delivered_qty'], 'pairs_pending': group['shoes_pair_delivery_pending_qty'], 'pairs_line_cancelled': group['shoes_pair_cancelled_qty']})
        
        for group in pairs_data_cancel:
            if not group['salesman_id'] or not group['shoes_campaign_id']: continue
            user_id, campaign_id = group['salesman_id'][0], group['shoes_campaign_id'][0]
            salesman_ids.add(user_id)
            entry = data_map[user_id]['campanias_data'][campaign_id]
            entry['pairs_order_cancelled'] = group['pairs_count']
        
        for group in reserved_data:
            user_id, campaign_id = group['salesman_id'], group['shoes_campaign_id']
            if not user_id or not campaign_id: continue
            salesman_ids.add(user_id)
            entry = data_map[user_id]['campanias_data'][campaign_id]
            entry['pairs_reserved'] = group['total_reserved'] or 0

        salesman_name_map = {u.id: u.name for u in self.env['res.users'].browse(list(salesman_ids))}
        for user_id, user_data in data_map.items():
            user_data['representante'] = salesman_name_map.get(user_id, 'N/A')

        # --- 3. Preparar datos para JSON y HTML ---
        analysis_html_parts = []
        data_for_json = []
        campaign_totals = defaultdict(lambda: {'nombre': '', 'netos': 0, 'fact_prevista': 0.0})
        base_camp_id = analysis.shoes_campaign_id.id
        
        # Crear una lista ordenada de IDs de campaña para asegurar el orden en el informe
        compare_camp_ids = analysis.shoes_campaign_ids.ids
        ordered_campaign_ids = [base_camp_id]
        for cid in compare_camp_ids:
            if cid != base_camp_id:
                ordered_campaign_ids.append(cid)

        sorted_user_data = sorted(data_map.values(), key=lambda u: u['representante'])

        for user_data in sorted_user_data:
            if base_camp_id not in user_data['campanias_data']:
                continue
            
            json_line_data = {'representante': user_data['representante'], 'campanias': []}
            
            # Iterar sobre las campañas en el orden definido para asegurar la consistencia
            for camp_id in ordered_campaign_ids:
                if camp_id in user_data['campanias_data']:
                    totals = user_data['campanias_data'][camp_id]
                    
                    total_vendidos = totals['pairs_count'] + totals['pairs_order_cancelled']
                    total_cancelados = totals['pairs_line_cancelled'] + totals['pairs_order_cancelled']
                    netos = total_vendidos - total_cancelados
                    asignados = totals['pairs_delivered'] + totals['pairs_reserved']
                    
                    camp_data_for_json = {
                        'campania_id': camp_id, 'campania_nombre': campaign_name_map.get(camp_id, "N/A"),
                        'pairs_count': totals['pairs_count'], 'total_vendidos': total_vendidos,
                        'total_cancelados': total_cancelados, 'netos': netos, 'asignados': asignados,
                        'pairs_delivered': totals['pairs_delivered'], 'pairs_pending': totals['pairs_pending'],
                        'total_vendido': totals['total_sales'], 'expected_revenue': totals['expected_revenue']
                    }
                    json_line_data['campanias'].append(camp_data_for_json)

                    campaign_totals[camp_id]['nombre'] = campaign_name_map.get(camp_id, 'N/A')
                    campaign_totals[camp_id]['netos'] += netos
                    campaign_totals[camp_id]['fact_prevista'] += totals['expected_revenue']
            
            if json_line_data['campanias']:
                data_for_json.append(json_line_data)
                analysis_html_parts.append(self._generate_line_html(json_line_data, base_camp_id, analysis.currency_id))

        # --- 4. Generar HTML de Resumen y preparar JSON final ---
        resume_html = self._generate_resume_html(campaign_totals, base_camp_id, analysis.shoes_campaign_ids)
        final_json_output = {
            'resumen_campañas': list(campaign_totals.values()),
            'detalle_representantes': data_for_json
        }

        # --- 5. Escribir los resultados ---
        analysis.write({
            'analysis_html': "".join(analysis_html_parts),
            'resume_html': resume_html,
            'data': final_json_output,
        })
        return True

    def _get_objective_perc_html(self, current, objective, style_str):
        if objective == 0: return f'<td class="text-end" style="{style_str} color: green;"><b>+&infin;%</b></td>' if current > 0 else f'<td class="text-end" style="{style_str}">-</td>'
        perc = current / objective
        color = 'green' if perc >= 1.0 else 'red'
        return f'<td class="text-end" style="{style_str} color: {color};"><b>{perc:.1%}</b></td>'

    def _get_servidos_perc_html(self, servidos, netos, style_str):
        if netos == 0: return f'<td class="text-end" style="{style_str}">-</td>'
        return f'<td class="text-end" style="{style_str}"><b>{(servidos / netos):.1%}</b></td>'

    def _get_asign_perc_html(self, asignados, netos, style_str):
        if netos == 0: return f'<td class="text-end" style="{style_str}">-</td>'
        perc = asignados / netos
        color = 'green' if perc >= 1.0 else 'inherit'
        return f'<td class="text-end" style="{style_str} color: {color};"><b>{perc:.1%}</b></td>'

    def _generate_line_html(self, data_dict, base_camp_id, currency_obj):
        all_camp_data = data_dict.get('campanias', [])
        base_data = next((c for c in all_camp_data if c.get('campania_id') == base_camp_id), None)
        if not base_data: return "" # No hay datos para la campaña base de este representante
        
        # Las campañas de comparación ya vienen ordenadas desde el paso anterior
        compare_data_list = [c for c in all_camp_data if c.get('campania_id') != base_camp_id]
        
        base_pairs, base_sales, base_netos, base_delivered, base_asignados = base_data.get('pairs_count', 0), base_data.get('total_vendido', 0.0), base_data.get('netos', 0), base_data.get('pairs_delivered', 0), base_data.get('asignados', 0)
        
        html_parts = [f"<div style='border: 2px solid #333; border-radius: 5px; margin-bottom: 30px; padding: 20px; background-color: #f0f0f0; page-break-inside: avoid;'>"]
        html_parts.append(f"<h2 style='font-size: 2em; font-weight: bold; margin-bottom: 20px;'>{html_escape(data_dict.get('representante', ''))}</h2>")
        
        html_parts.append('<table class="table table-sm o_main_table" style="width: 100%; font-size: 0.9em;">')
        html_parts.append(f'<thead><tr style="font-size: 0.85em; color: #555;"><th>Campaña</th><th class="text-end">Total Vend.</th><th class="text-end">Total Canc.</th><th class="text-end">Netos</th><th class="text-end">Asignados</th><th class="text-end">% Asign.</th><th class="text-end">Servidos</th><th class="text-end">% Servidos</th><th class="text-end">Pendientes</th><th class="text-end">Fact. Prevista</th><th class="text-end">%Pares</th><th class="text-end">%Ventas</th></tr></thead>')
        html_parts.append('<tbody>')
        
        html_parts.append(f'<tr><td><b>{html_escape(base_data.get("campania_nombre", "N/A"))} (Actual)</b></td><td class="text-end"><b>{base_data.get("total_vendidos", 0)}</b></td><td class="text-end"><b>{base_data.get("total_cancelados", 0)}</b></td><td class="text-end"><b>{base_netos}</b></td><td class="text-end"><b>{base_asignados}</b></td>{self._get_asign_perc_html(base_asignados, base_netos, "")}<td class="text-end"><b>{base_delivered}</b></td>{self._get_servidos_perc_html(base_delivered, base_netos, "")}<td class="text-end"><b>{base_data.get("pairs_pending", 0)}</b></td><td class="text-end"><b>{formatLang(self.env, base_data.get("expected_revenue", 0.0), currency_obj=currency_obj)}</b></td><td class="text-end">-</td><td class="text-end">-</td></tr>')
        
        for camp_data in compare_data_list:
            objective_pairs, objective_sales, objective_netos, objective_delivered, objective_asignados = camp_data.get('pairs_count', 0), camp_data.get('total_vendido', 0.0), camp_data.get('netos', 0), camp_data.get('pairs_delivered', 0), camp_data.get('asignados', 0)
            html_parts.append(f'<tr><td>{html_escape(camp_data.get("campania_nombre", "N/A"))} (Objetivo)</td><td class="text-end">{camp_data.get("total_vendidos", 0)}</td><td class="text-end">{camp_data.get("total_cancelados", 0)}</td><td class="text-end">{objective_netos}</td><td class="text-end">{objective_asignados}</td>{self._get_asign_perc_html(objective_asignados, objective_netos, "")}<td class="text-end">{objective_delivered}</td>{self._get_servidos_perc_html(objective_delivered, objective_netos, "")}<td class="text-end">{camp_data.get("pairs_pending", 0)}</td><td class="text-end">{formatLang(self.env, camp_data.get("expected_revenue", 0.0), currency_obj=currency_obj)}</td>{self._get_objective_perc_html(base_pairs, objective_pairs, "")}{self._get_objective_perc_html(base_sales, objective_sales, "")}</tr>')
        
        html_parts.append('</tbody></table></div>')
        return "".join(html_parts)
