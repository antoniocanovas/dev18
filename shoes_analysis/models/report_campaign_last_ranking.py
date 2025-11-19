from odoo import models, api
from collections import defaultdict

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def _compute_campaign_last_ranking(self):
        """
        Orquesta la creación del informe que agrupa productos por el ranking de su horma.
        """
        for analysis in self:
            campaign_id = analysis.shoes_campaign_id.id
            
            horma_lines = self.env['shoes.ranking'].search([
                ('shoes_campaign_id', '=', campaign_id),
                ('shoes_last_id', '!=', False)
            ], order='ranking asc')

            product_lines = self.env['shoes.ranking'].search([
                ('shoes_campaign_id', '=', campaign_id),
                ('product_tmpl_id', '!=', False)
            ])

            analysis._generate_campaign_last_ranking_html(horma_lines, product_lines)
        
        return True

    def _generate_campaign_last_ranking_html(self, horma_lines, product_lines):
        """
        Genera el HTML y los datos JSON agrupando productos por horma.
        """
        self.ensure_one()
        analysis = self

        if not horma_lines:
            analysis.write({
                'analysis_html': "<p>No hay datos de ranking de hormas para mostrar.</p>",
                'data': False
            })
            return

        products_by_last = defaultdict(list)
        for prod_line in product_lines:
            if prod_line.product_tmpl_id.shoes_last_id:
                products_by_last[prod_line.product_tmpl_id.shoes_last_id.id].append(prod_line)

        html_parts = []
        data_for_json = []
        
        style_horma_group = "border: 2px solid #666; border-radius: 5px; margin-bottom: 30px; padding: 20px; background-color: #f9f9f9;"
        style_horma_header = "font-size: 32px; font-weight: bold; margin: 0 0 20px 0; border-bottom: 1px solid #ccc; padding-bottom: 10px;"
        style_total_quantity = "float: right; font-size: 32px; font-weight: bold;"

        for horma_line in horma_lines:
            horma_data_for_json = horma_line.read(['name', 'ranking', 'pairs_count_net', 'shoes_last_id'])[0]
            horma_data_for_json['products'] = []
            
            html_parts.append(f"<div style='{style_horma_group}'>")
            total_pairs_html = f"<div style='{style_total_quantity}'>{int(horma_line.pairs_count_net)}</div>"
            html_parts.append(f"<h2 style='{style_horma_header}'>{horma_line.shoes_last_id.name or 'N/A'} {total_pairs_html}</h2>")
            
            products_for_this_last = products_by_last.get(horma_line.shoes_last_id.id, [])
            sorted_products = sorted(products_for_this_last, key=lambda p: p.ranking)

            if not sorted_products:
                html_parts.append("<p>No hay productos con ranking para esta horma.</p>")
            else:
                product_data_list = []
                for product_line in sorted_products:
                    html_parts.append(self._generate_product_card_html(product_line))
                    line_data = product_line.read(['name', 'ranking', 'pairs_count_net', 'product_tmpl_id'])[0]
                    line_data['colors'] = self._get_color_statistics(product_line.product_tmpl_id, product_line.shoes_campaign_id)
                    product_data_list.append(line_data)
                horma_data_for_json['products'] = product_data_list

            html_parts.append("</div>")
            data_for_json.append(horma_data_for_json)

        analysis.write({
            'analysis_html': "\n".join(html_parts),
            'data': data_for_json
        })
