# -*- coding: utf-8 -*-
from odoo import models
import json
import base64
from collections import OrderedDict

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def _compute_stock_available(self):
        self.ensure_one()
        
        # Domain for products
        product_domain = [
            ('virtual_available', '>', 0),
            ('shoes_campaign_ids', 'in', self.shoes_campaign_id.id)
        ]
        products = self.env['product.product'].search(product_domain)

        if not products:
            self.analysis_html = "<p>No products found with available stock in the selected campaign.</p>"
            return

        # Domain for stock moves
        move_line_domain = [
            ('product_id', 'in', products.ids),
            ('location_dest_id.usage', '=', 'internal'),
            ('quantity', '>', 0)
        ]
        move_lines = self.env['stock.move.line'].search(move_line_domain)

        if not move_lines:
            self.analysis_html = "<p>No stock move lines found for products with available stock in the selected campaign.</p>"
            return

        # Grouping data
        grouped_data = {}
        for line in move_lines:
            product_tmpl = line.product_id.product_tmpl_id
            model = product_tmpl.shoes_model_material or "Undefined Model"
            color = line.product_id.color_value_id.name or "Undefined Color"
            assortment_value = line.product_id.assortment_attribute_id
            assortment_name = assortment_value.name or "Undefined Assortment"
            
            if model not in grouped_data:
                image_base64 = ''
                if product_tmpl.image_128:
                    image_base64 = product_tmpl.image_128.decode('utf-8')

                grouped_data[model] = {
                    "product_name": product_tmpl.name,
                    "category": product_tmpl.categ_id.name,
                    "image": image_base64,
                    "colors": {}
                }
            
            colors = grouped_data[model]["colors"]
            if color not in colors:
                colors[color] = {}
            
            if assortment_name not in colors[color]:
                breakdown = OrderedDict()
                if assortment_value and assortment_value.assortment_id:
                    sorted_lines = sorted(assortment_value.assortment_id.line_ids, key=lambda l: l.value_id.name)
                    for assortment_line in sorted_lines:
                        breakdown[assortment_line.value_id.name] = assortment_line.quantity
                
                colors[color][assortment_name] = {
                    "quantity": 0,
                    "breakdown": breakdown
                }
            
            colors[color][assortment_name]["quantity"] += line.quantity
        
        self.data = json.dumps(grouped_data)
        self._generate_stock_available_html()

    def _generate_stock_available_html(self):
        self.ensure_one()
        if not self.data:
            self.analysis_html = "<p>No data to generate the report.</p>"
            return

        data = json.loads(self.data)
        
        html_parts = ['<div class="container">']
        
        style_model_group = "border: 2px solid #666; border-radius: 5px; margin-bottom: 20px; padding: 15px; background-color: #f9f9f9; page-break-inside: avoid; overflow: hidden;"
        style_product_info = "font-size: 16px; margin-bottom: 15px; float: left; margin-left: 20px;"
        style_image = "float: left; width: 128px; height: 128px;"
        style_model_header = "font-size: 24px; font-weight: bold; color: #000080;"
        style_table = "width: 100%; border-collapse: collapse; margin-top: 10px; clear: both;"
        style_th = "background-color: #f2f2f2; text-align: left; padding: 8px; border-bottom: 2px solid #ddd;"
        style_th_center = style_th + " text-align: center;"
        style_td = "padding: 8px; border-bottom: 1px solid #ddd; vertical-align: top;"
        style_td_center = style_td + " text-align: center;"
        
        # Styles for breakdown table
        style_breakdown_table = "width: 100%; border-collapse: collapse; text-align: center;"
        style_breakdown_th = "background-color: #e0e0e0; padding: 4px; font-weight: bold;"
        style_breakdown_td = "padding: 4px;"

        for model, model_data in data.items():
            html_parts.append(f'<div style="{style_model_group}">')
            
            if model_data.get("image"):
                html_parts.append(f'<img src="data:image/png;base64,{model_data["image"]}" style="{style_image}"/>')

            html_parts.append(f'<div style="{style_product_info}">')
            html_parts.append(f'<h2 style="{style_model_header}">{model}</h2>')
            html_parts.append(f'<strong>Product:</strong> {model_data["product_name"]}<br/>')
            html_parts.append(f'<strong>Category:</strong> {model_data["category"]}')
            html_parts.append('</div>')
            
            html_parts.append(f'<table style="{style_table}">')
            html_parts.append(f'<thead><tr><th style="{style_th}">Color</th><th style="{style_th_center}">Assortment</th><th style="{style_th_center}">Quantity</th><th style="{style_th_center}">Pack</th><th style="{style_th_center}">Pairs</th></tr></thead>')
            html_parts.append('<tbody>')

            for color, assortments in model_data["colors"].items():
                rowspan = len(assortments)
                first_row = True
                for assortment, assortment_data in assortments.items():
                    quantity = int(assortment_data["quantity"])
                    breakdown = assortment_data.get("breakdown", {})
                    
                    total_pairs_in_breakdown = sum(breakdown.values())
                    total_pairs = int(total_pairs_in_breakdown * quantity)

                    breakdown_html = f'<table style="{style_breakdown_table}">'
                    breakdown_html += '<tr>' + "".join([f'<th style="{style_breakdown_th}">{size}</th>' for size in breakdown.keys()]) + '</tr>'
                    breakdown_html += '<tr>' + "".join([f'<td style="{style_breakdown_td}">{qty}</td>' for qty in breakdown.values()]) + '</tr>'
                    breakdown_html += '</table>'

                    if first_row:
                        html_parts.append('<tr>')
                        html_parts.append(f'<td style="{style_td}" rowspan="{rowspan}">{color}</td>')
                        html_parts.append(f'<td style="{style_td_center}">{assortment}</td>')
                        html_parts.append(f'<td style="{style_td_center}">{quantity}</td>')
                        html_parts.append(f'<td style="{style_td}">{breakdown_html}</td>')
                        html_parts.append(f'<td style="{style_td_center}">{total_pairs}</td>')
                        html_parts.append('</tr>')
                        first_row = False
                    else:
                        html_parts.append('<tr>')
                        html_parts.append(f'<td style="{style_td_center}">{assortment}</td>')
                        html_parts.append(f'<td style="{style_td_center}">{quantity}</td>')
                        html_parts.append(f'<td style="{style_td}">{breakdown_html}</td>')
                        html_parts.append(f'<td style="{style_td_center}">{total_pairs}</td>')
                        html_parts.append('</tr>')

            html_parts.append('</tbody></table>')
            html_parts.append('</div>')

        html_parts.append('</div>')
        self.analysis_html = "".join(html_parts)
