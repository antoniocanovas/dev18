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

    def _compute_salesman_customers(self):
        """
        Genera el informe HTML y los datos JSON para la comparativa de ventas por cliente de un representante.
        """
        self.ensure_one()
        analysis = self
        
        main_campaign = analysis.shoes_campaign_id
        all_campaigns = main_campaign | analysis.shoes_campaign_ids
        if not all_campaigns:
            analysis.analysis_html = "<p>No hay campañas para comparar.</p>"
            return

        domain = [
            ('order_id.shoes_campaign_id', 'in', all_campaigns.ids),
            ('order_id.state', 'in', ['sale', 'done']),
            ('order_id.user_id', '=', analysis.referrer_id.id),
            '|',
                '&', ('product_id.is_pair', '=', True), ('product_id.product_tmpl_id', '!=', False),
                '&', ('product_id.is_assortment', '=', True), ('product_id.product_tmpl_single_id', '!=', False),
        ]
        
        sales_data = self.env['sale.order.line'].read_group(
            domain,
            fields=['price_subtotal', 'product_uom_qty', 'pairs_count', 'shoes_pair_cancelled_qty'],
            groupby=['order_partner_id', 'shoes_campaign_id'],
            lazy=False
        )

        data_map = defaultdict(lambda: defaultdict(lambda: {'net_pairs': 0, 'net_sales': 0}))
        all_partner_ids = set()

        for group in sales_data:
            partner_id = group['order_partner_id'][0]
            campaign_id = group['shoes_campaign_id'][0]
            all_partner_ids.add(partner_id)
            net_pairs = (group['product_uom_qty'] * group.get('pairs_count', 1)) + group.get('shoes_pair_cancelled_qty', 0)
            data_map[partner_id][campaign_id]['net_pairs'] += net_pairs
            data_map[partner_id][campaign_id]['net_sales'] += group['price_subtotal']

        html_parts, json_output = [], []
        partners = self.env['res.partner'].browse(list(all_partner_ids)).sorted('name')
        
        base_camp_id = analysis.shoes_campaign_id.id

        for partner in partners:
            customer_html = [f"<div style='border: 2px solid #333; border-radius: 5px; margin-bottom: 30px; padding: 20px; background-color: #f0f0f0; page-break-inside: avoid;'>"]
            customer_html.append(f"<h2 style='font-size: 2em; font-weight: bold; margin-bottom: 0px;'>{html_escape(partner.name)}</h2>")
            if analysis.referrer_id:
                customer_html.append(f"<div style='margin-bottom: 20px;'><span class='badge rounded-pill text-bg-primary' style='font-size: 0.8em;'>{html_escape(analysis.referrer_id.name)}</span></div>")
            else:
                customer_html.append("<div style='margin-bottom: 20px;'></div>")
            customer_json = {'partner_id': partner.id, 'partner_name': partner.name, 'brands': []}

            partner_campaigns = self.env['project.project'].browse(list(data_map[partner.id].keys()))
            campaigns_by_brand = defaultdict(lambda: self.env['project.project'])
            for camp in partner_campaigns:
                campaigns_by_brand[camp.product_brand_id] |= camp

            for brand, campaigns in campaigns_by_brand.items():
                brand_html = [f"<div style='margin-left: 20px; margin-bottom: 20px; page-break-inside: avoid;'>"]
                brand_html.append(f"<h3 style='font-size: 1.5em; font-weight: 600; border-bottom: 1px solid #ccc; padding-bottom: 5px;'>Marca: {html_escape(brand.name)}</h3>")
                brand_json = {'brand_id': brand.id, 'brand_name': brand.name, 'campaigns': []}

                sorted_campaigns = campaigns.sorted('date', reverse=True)
                ordered_campaigns = sorted(sorted_campaigns, key=lambda c: c.id != base_camp_id)

                main_campaign_stats = data_map[partner.id].get(base_camp_id, {'net_pairs': 0, 'net_sales': 0})

                style_th = "padding: 8px; border-bottom: 2px solid #333;"
                style_camp = style_th + " width: 40%;"
                style_pairs = style_th + " width: 15%;"
                style_sales = style_th + " width: 15%;"
                style_perc_pairs = style_th + " width: 15%;"
                style_perc_sales = style_th + " width: 15%;"

                brand_html.append(f"<table class='table table-sm' style='font-size: 0.9em; table-layout: fixed;'><thead><tr>"
                                  f"<th class='text-start' style='{style_camp}'>Campaña</th>"
                                  f"<th class='text-end' style='{style_pairs}'>Pares Netos</th>"
                                  f"<th class='text-end' style='{style_sales}'>Ventas Netas</th>"
                                  f"<th class='text-end' style='{style_perc_pairs}'>% Obj. Pares</th>"
                                  f"<th class='text-end' style='{style_perc_sales}'>% Obj. Ventas</th>"
                                  f"</tr></thead><tbody>")
                
                for camp in ordered_campaigns:
                    stats = data_map[partner.id][camp.id]
                    is_main = (camp.id == base_camp_id)
                    tag = "b" if is_main else "span"
                    
                    row_html = f"<tr><td class='text-start'><{tag}>{html_escape(camp.display_name)}</{tag}></td>"
                    row_html += f"<td class='text-end'><{tag}>{int(stats['net_pairs'])}</{tag}></td>"
                    row_html += f"<td class='text-end'><{tag}>{formatLang(self.env, stats['net_sales'], currency_obj=analysis.currency_id)}</{tag}></td>"
                    
                    if is_main:
                        row_html += "<td class='text-end'>-</td><td class='text-end'>-</td>"
                    else:
                        row_html += self._get_objective_perc_html(main_campaign_stats['net_pairs'], stats['net_pairs'], "padding: 8px;")
                        row_html += self._get_objective_perc_html(main_campaign_stats['net_sales'], stats['net_sales'], "padding: 8px;")
                    
                    row_html += "</tr>"
                    brand_html.append(row_html)
                    
                    campaign_json = {'campaign_id': camp.id, 'campaign_name': camp.display_name, 'net_pairs': stats['net_pairs'], 'net_sales': stats['net_sales']}
                    brand_json['campaigns'].append(campaign_json)

                brand_html.append("</tbody></table></div>")
                customer_html.extend(brand_html)
                customer_json['brands'].append(brand_json)

            customer_html.append("</div>")
            html_parts.extend(customer_html)
            json_output.append(customer_json)

        analysis.write({
            'analysis_html': "".join(html_parts),
            'data': json_output
        })
        return True
