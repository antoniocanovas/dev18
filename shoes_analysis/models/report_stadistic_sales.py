from odoo import models, fields, api
from odoo.tools import float_is_zero
from odoo.tools.misc import formatLang
from collections import defaultdict
import qrcode
import io
import base64

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    # -----------------------------------------------------------------
    # INFORME "STATISTIC SALES"
    # -----------------------------------------------------------------

    def _compute_stadistic_sales(self):
        """
        Método principal que orquesta la actualización de datos y la
        generación del informe HTML de estadísticas.
        """
        for analysis in self:
            # 1. Llama al motor principal para que haga todo el trabajo de cálculo
            self.env['shoes.ranking']._update_ranking_for_campaign(analysis.shoes_campaign_id)

            # 2. Busca explícitamente las líneas de ranking de PRODUCTOS
            product_ranking_lines = self.env['shoes.ranking'].search([
                ('shoes_campaign_id', '=', analysis.shoes_campaign_id.id),
                ('product_tmpl_id', '!=', False)
            ])

            # 3. Genera su HTML específico solo con esas líneas
            analysis._generate_stadistic_sale_html(product_ranking_lines)

        return True

    # -----------------------------------------------------------------
    # MÉTODO 2: GENERACIÓN DE HTML (NUEVO FORMATO)
    # -----------------------------------------------------------------

    def _generate_stadistic_sale_html(self, ranking_lines):
        """
        Genera el HTML (formato "ficha") para cada línea de ranking
        y lo concatena en el campo 'analysis_html'.
        """
        self.ensure_one()
        analysis = self

        if not ranking_lines:
            analysis.analysis_html = "<p>No hay datos de estadísticas para mostrar.</p>"
            return

        html_cards = []

        # Estilos
        style_card = "border: 1px solid #ddd; margin-bottom: 20px; padding: 15px; overflow: hidden; font-family: sans-serif;"
        style_left = "float: left; width: 20%; text-align: center; min-height: 180px;"
        style_right = "float: left; width: 78%; margin-left: 2%;"
        style_header = "font-size: 24px; font-weight: bold; margin: 0; padding: 0;"
        style_subheader = "font-size: 18px; color: #555; margin: 0 0 15px 0;"
        style_table = "width: 100%; border-collapse: collapse; font-size: 12px;"
        style_th = "border-bottom: 2px solid #333; padding: 6px; text-align: left;"
        style_td = "border-bottom: 1px solid #ccc; padding: 6px;"
        style_td_num = f"{style_td} text-align: right; font-weight: bold;"

        for line in ranking_lines:
            img_html = ""
            if line.image:
                img_base64 = line.image.decode('utf-8')
                img_html = f"<img src='data:image/png;base64,{img_base64}' style='max-width: 100%; height: auto; max-height: 180px; object-fit: contain;'/>"

            formatted_pairs = f"{line.pairs_count_net} p"

            # --- Generación del QR Code ---
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

            # --- HTML de la ficha con la nueva estructura ---
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

            color_stats = self._get_color_statistics(
                line.product_tmpl_id,
                line.shoes_campaign_id
            )

            card_html += f"""
            <table style='{style_table}'>
                <thead>
                    <tr>
                        <th style='{style_th}'>Color</th>
                        <th style='{style_th} text-align: right;'>Vendido</th>
                        <th style='{style_th} text-align: right;'>En Produccion</th>
                        <th style='{style_th} text-align: right;'>Stock Estimado</th>
                    </tr>
                </thead>
                <tbody>
            """

            total_vendido = 0
            total_produccion = 0

            if not color_stats:
                card_html += f"<tr><td colspan='4' style='{style_td} text-align: center;'>Sin desglose de color</td></tr>"

            for stat in color_stats:
                total_vendido += stat['sold']
                total_produccion += stat['produced']
                row_style = style_td
                if stat['sold'] >= 100:
                    row_style = f"{style_td} background-color: #f0f0f0;"
                card_html += f"""
                <tr>
                    <td style='{row_style}'>{stat['color_name'] or ''}</td>
                    <td style='{row_style} text-align: right; font-weight: bold;'>{stat['sold']}</td>
                    <td style='{row_style} text-align: right;'>{stat['produced']}</td>
                    <td style='{row_style} text-align: right;'>{stat['stock']}</td>
                </tr>
                """

            card_html += f"""
                </tbody>
                <tfoot>
                    <tr style='background-color: #ddd; font-weight: bold;'>
                        <td style='{style_td}'>TOTALES</td>
                        <td style='{style_td_num}'>{total_vendido}</td>
                        <td style='{style_td_num}'>{total_produccion}</td>
                        <td style='{style_td}'></td>
                    </tr>
                </tfoot>
            </table>
            </div>
                        <div style='clear: both;'></div>
                    </div>
                </div>
                <div style='clear: both;'></div>
            </div>
            """
            html_cards.append(card_html)

        analysis.analysis_html = "\n".join(html_cards)

    # -----------------------------------------------------------------
    # MÉTODO 3: AYUDANTE PARA ESTADÍSTICAS DE COLOR (CORREGIDO)
    # -----------------------------------------------------------------

    def _get_color_statistics(self, product_tmpl, campaign):
        """
        Método ayudante que devuelve el desglose de ventas, producción
        y stock por color para un producto y campaña específicos.
        """
        domain = [
            ('order_id.shoes_campaign_id', '=', campaign.id),
            ('order_id.state', 'in', ['sale', 'done']),
            ('color_value_id', '!=', False),
            '|',
                '&',
                    ('product_id.is_pair', '=', True),
                    ('product_id.product_tmpl_id', '=', product_tmpl.id),
                '&',
                    ('product_id.is_assortment', '=', True),
                    ('product_id.product_tmpl_single_id', '=', product_tmpl.id),
        ]
        sale_lines = self.env['sale.order.line'].search(domain)

        color_aggr = defaultdict(lambda: {'sold': 0, 'produced': 0})
        color_map = {}

        for line in sale_lines:
            color_val = line.color_value_id
            key = color_val.id
            if key not in color_map:
                color_map[key] = color_val
            color_aggr[key]['sold'] += (line.product_uom_qty * line.pairs_count) - line.shoes_pair_cancelled_qty
            color_aggr[key]['produced'] += line.qty_delivered * line.pairs_count

        final_stats = []
        color_values = self.env['product.attribute.value'].browse(color_map.keys())

        for color_val in color_values:
            key = color_val.id
            data = color_aggr[key]
            variant = self.env['product.product'].search([
                ('product_tmpl_id', '=', product_tmpl.id),
                ('product_template_attribute_value_ids.product_attribute_value_id', '=', color_val.id)
            ], limit=1)
            stock_estimado = 0
            if variant:
                stock_estimado = variant.virtual_available
            final_stats.append({
                'color_name': color_val.name,
                'sold': data['sold'],
                'produced': data['produced'],
                'stock': stock_estimado,
            })

        return sorted(final_stats, key=lambda x: x['sold'], reverse=True)
