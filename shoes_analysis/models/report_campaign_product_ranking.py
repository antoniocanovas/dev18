from odoo import models, fields, api
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang
from collections import defaultdict
import qrcode
import io
import base64

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def _compute_campaign_product_ranking(self):
        """
        Genera el informe HTML y los datos JSON para el ranking de productos por campaña.
        """
        for analysis in self:
            ranking_lines_domain = [
                ('shoes_campaign_id', '=', analysis.shoes_campaign_id.id),
                ('product_tmpl_id', '!=', False)
            ]
            product_ranking_lines = self.env['shoes.ranking'].search(ranking_lines_domain)
            analysis._generate_campaign_product_ranking_html(product_ranking_lines)
        return True

    def _generate_campaign_product_ranking_html(self, ranking_lines):
        """
        Genera el HTML y los datos JSON para el ranking de productos por campaña.
        """
        self.ensure_one()
        if not ranking_lines:
            self.write({
                'analysis_html': "<p>No hay datos de ranking para mostrar.</p>",
                'data': False
            })
            return
        
        html_cards = [self._generate_product_card_html(line) for line in ranking_lines]
        
        data_for_json = []
        for line in ranking_lines:
            line_data = line.read([
                'name', 'ranking', 'pairs_count_sale', 'pairs_count_cancel', 
                'pairs_count_net', 'sale_net_amount', 'currency_id',
                'product_tmpl_id', 'shoes_model_material_id', 'shoes_campaign_id'
            ])[0]
            line_data['colors'] = self._get_color_statistics(line.product_tmpl_id, line.shoes_campaign_id)
            data_for_json.append(line_data)

        self.write({
            'analysis_html': "\n".join(html_cards),
            'data': data_for_json
        })

    def _generate_product_card_html(self, line):
        # ... (el resto del método no cambia)
        style_card = "border: 1px solid #ddd; margin-bottom: 20px; padding: 15px; overflow: hidden; font-family: sans-serif; background-color: #fff; page-break-inside: avoid;"
        style_left = "float: left; width: 20%; text-align: center; min-height: 180px;"
        style_right = "float: left; width: 78%; margin-left: 2%;"
        style_header = "font-size: 24px; font-weight: bold; margin: 0; padding: 0;"
        style_subheader = "font-size: 18px; color: #555; margin: 0 0 15px 0;"
        style_table = "width: 100%; border-collapse: collapse; font-size: 0.9em;"
        style_th = "border-bottom: 2px solid #333; padding: 6px; text-align: left;"
        style_td = "border-bottom: 1px solid #ccc; padding: 6px;"
        style_td_num = f"{style_td} text-align: right; font-weight: bold;"

        img_html = ""
        if line.image:
            img_base64 = line.image.decode('utf-8')
            img_html = f"<img src='data:image/png;base64,{img_base64}' style='max-width: 100%; height: auto; max-height: 180px; object-fit: contain;'/>"

        formatted_pairs = f"{line.pairs_count_net} p"

        qr_code_html = ""
        if line.shoes_model_material_id and line.shoes_model_material_id.shoes_url:
            try:
                qr = qrcode.QRCode(version=1, box_size=4, border=4)
                qr.add_data(line.shoes_model_material_id.shoes_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffered = io.BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                qr_code_html = f"<img src='data:image/png;base64,{img_str}' style='width: 100px; height: 100px;'/>"
            except Exception:
                qr_code_html = "<span>Error QR</span>"

        card_html = f"""
        <div style='{style_card}'>
            <div style='{style_left}'>{img_html}</div>
            <div style='{style_right}'>
                <div>
                    <h2 style='{style_header}; float: left;'>{line.shoes_model_material_id.name or ''}</h2>
                    <h2 style='{style_header}; float: right; color: #888;'>P.V. <span style='color: #000;'>{line.ranking or 0}</span></h2>
                    <h2 style='{style_header}; float: right; margin-right: 30px;'>{formatted_pairs}</h2>
                    <div style='clear: both;'></div>
                    <h3 style='{style_subheader}'>{line.product_tmpl_id.name or ''}</h3>
                </div>
                <div>
                    <div style='float: left; width: 20%; text-align: center; padding-top: 10px;'>
                        {qr_code_html}
                    </div>
                    <div style='float: left; width: 78%;'>
        """

        color_stats = self._get_color_statistics(line.product_tmpl_id, line.shoes_campaign_id)
        
        table_html = f"<table style='{style_table}'><thead><tr>"
        table_html += f"<th style='{style_th}'>Color</th>"
        table_html += f"<th style='{style_th} text-align: right;'>Vendido</th>"
        table_html += f"<th style='{style_th} text-align: right;'>En Produccion</th>"
        table_html += f"<th style='{style_th} text-align: right;'>Stock Estimado</th>"
        table_html += "</tr></thead><tbody>"

        total_vendido, total_produccion = 0, 0
        if not color_stats:
            table_html += f"<tr><td colspan='4' style='{style_td} text-align: center;'>Sin desglose de color</td></tr>"
        else:
            for stat in color_stats:
                total_vendido += stat['sold']
                total_produccion += stat['produced']
                row_style = style_td + (' background-color: #f0f0f0;' if stat['sold'] >= 100 else '')
                table_html += f"""
                    <tr>
                        <td style='{row_style}'>{stat['color_name'] or ''}</td>
                        <td style='{row_style} text-align: right; font-weight: bold;'>{stat['sold']}</td>
                        <td style='{row_style} text-align: right;'>{stat['produced']}</td>
                        <td style='{row_style} text-align: right;'>{stat['stock']}</td>
                    </tr>
                """
        
        table_html += f"""
            </tbody><tfoot>
                <tr style='background-color: #ddd; font-weight: bold;'>
                    <td style='{style_td}'>TOTALES</td>
                    <td style='{style_td_num}'>{total_vendido}</td>
                    <td style='{style_td_num}'>{total_produccion}</td>
                    <td style='{style_td}'></td>
                </tr>
            </tfoot></table>
        """
        
        card_html += table_html
        card_html += "</div><div style='clear: both;'></div></div></div><div style='clear: both;'></div></div>"
        return card_html

    def _get_color_statistics(self, product_tmpl, campaign):
        domain = [
            ('order_id.shoes_campaign_id', '=', campaign.id),
            ('order_id.state', 'in', ['sale', 'done']),
            ('color_value_id', '!=', False),
            '|',
                '&', ('product_id.is_pair', '=', True), ('product_id.product_tmpl_id', '=', product_tmpl.id),
                '&', ('product_id.is_assortment', '=', True), ('product_id.product_tmpl_single_id', '=', product_tmpl.id),
        ]
        sale_lines = self.env['sale.order.line'].search(domain)
        color_aggr = defaultdict(lambda: {'sold': 0, 'produced': 0})
        color_map = {}
        for line in sale_lines:
            color_val = line.color_value_id
            key = color_val.id
            if key not in color_map: color_map[key] = color_val
            color_aggr[key]['sold'] += (line.product_uom_qty * line.pairs_count) - line.shoes_pair_cancelled_qty
            color_aggr[key]['produced'] += line.qty_delivered * line.pairs_count
        
        final_stats = []
        for color_val in self.env['product.attribute.value'].browse(color_map.keys()):
            key = color_val.id
            data = color_aggr[key]
            variant = self.env['product.product'].search([
                ('product_tmpl_id', '=', product_tmpl.id),
                ('product_template_attribute_value_ids.product_attribute_value_id', '=', color_val.id)
            ], limit=1)
            stock_estimado = variant.virtual_available if variant else 0
            final_stats.append({
                'color_name': color_val.name,
                'sold': data['sold'], 'produced': data['produced'], 'stock': stock_estimado,
            })
        return sorted(final_stats, key=lambda x: x['sold'], reverse=True)
