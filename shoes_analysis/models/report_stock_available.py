# -*- coding: utf-8 -*-
from odoo import models
import json
import base64
from collections import OrderedDict

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def _compute_stock_available(self):
        self.ensure_one()
        
        # Domain for assortment templates
        assortment_tmpls = self.env['product.template'].search([
            ('is_assortment', '=', True),
            ('shoes_campaign_ids', 'in', self.shoes_campaign_id.id)
        ])

        grouped_data = {}
        for tmpl in assortment_tmpls:
            # Check for stock in assortments or single pairs before creating the model entry
            assortment_products_with_stock = tmpl.product_variant_ids.filtered(lambda p: p.virtual_available > 0)
            pair_products_with_stock = self.env['product.product']
            if tmpl.product_tmpl_single_id:
                pair_products_with_stock = tmpl.product_tmpl_single_id.product_variant_ids.filtered(lambda p: p.virtual_available > 0)

            if not assortment_products_with_stock and not pair_products_with_stock:
                continue

            model = tmpl.shoes_model_material or "Undefined Model"
            
            # Initialize model data
            image_base64 = ''
            if tmpl.image_128:
                image_base64 = tmpl.image_128.decode('utf-8')
            grouped_data[model] = {
                "product_tmpl_id": tmpl.id,
                "product_name": tmpl.name,
                "category": tmpl.categ_id.name,
                "image": image_base64,
                "colors": {}
            }

            # Process assortments with stock
            for product in assortment_products_with_stock:
                color = product.color_value_id.name or "Undefined Color"
                if color not in grouped_data[model]["colors"]:
                    grouped_data[model]["colors"][color] = {"assortments": {}, "pairs": {}}

                assortment_value = product.assortment_attribute_id
                assortment_name = assortment_value.name or "Undefined Assortment"
                
                breakdown = OrderedDict()
                if assortment_value and assortment_value.assortment_id:
                    sorted_lines = sorted(assortment_value.assortment_id.line_ids, key=lambda l: l.value_id.name)
                    for assortment_line in sorted_lines:
                        breakdown[assortment_line.value_id.name] = assortment_line.quantity
                
                grouped_data[model]["colors"][color]["assortments"][assortment_name] = {
                    "quantity": product.virtual_available,
                    "breakdown": breakdown
                }

            # Process single pairs with stock
            for product in pair_products_with_stock:
                color = product.color_value_id.name or "Undefined Color"
                if color not in grouped_data[model]["colors"]:
                     grouped_data[model]["colors"][color] = {"assortments": {}, "pairs": {}}
                
                size = product.size_value_id.name or "Undefined Size"
                if size not in grouped_data[model]["colors"][color]["pairs"]:
                    grouped_data[model]["colors"][color]["pairs"][size] = 0
                grouped_data[model]["colors"][color]["pairs"][size] += product.virtual_available
        
        if not grouped_data:
            self.analysis_html = "<p>No products with available stock found in the selected campaign.</p>"
            return

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

            product_link = f"/web#id={model_data['product_tmpl_id']}&model=product.template&view_type=form"
            
            html_parts.append(f'<div style="{style_product_info}">')
            html_parts.append(f'<h2 style="{style_model_header}">{model}</h2>')
            html_parts.append(f'<strong>Product:</strong> <a href="{product_link}" target="_blank">{model_data["product_name"]}</a><br/>')
            html_parts.append(f'<strong>Category:</strong> {model_data["category"]}')
            html_parts.append('</div>')
            
            html_parts.append(f'<table style="{style_table}">')
            html_parts.append(f'<thead><tr><th style="{style_th}">Color</th><th style="{style_th_center}">Assortment</th><th style="{style_th_center}">Quantity</th><th style="{style_th_center}">Pack</th><th style="{style_th_center}">Pairs</th></tr></thead>')
            html_parts.append('<tbody>')

            for color, color_data in model_data["colors"].items():
                assortments = color_data.get("assortments", {})
                pairs = color_data.get("pairs", {})
                
                # Calculate rowspan
                rowspan = len(assortments)
                if pairs:
                    rowspan += 1

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

                # Single pairs summary line
                if pairs:
                    total_pairs_quantity = sum(pairs.values())
                    pack_html = f'<table style="{style_breakdown_table}">'
                    pack_html += '<tr>' + "".join([f'<th style="{style_breakdown_th}">{size}</th>' for size in sorted(pairs.keys())]) + '</tr>'
                    pack_html += '<tr>' + "".join([f'<td style="{style_breakdown_td}">{pairs[size]}</td>' for size in sorted(pairs.keys())]) + '</tr>'
                    pack_html += '</table>'

                    html_parts.append('<tr>')
                    if first_row:
                         html_parts.append(f'<td style="{style_td}" rowspan="{rowspan}">{color}</td>')
                    html_parts.append(f'<td style="{style_td_center}">-</td>')
                    html_parts.append(f'<td style="{style_td_center}">{int(total_pairs_quantity)}</td>')
                    html_parts.append(f'<td style="{style_td}">{pack_html}</td>')
                    html_parts.append(f'<td style="{style_td_center}">{int(total_pairs_quantity)}</td>')
                    html_parts.append('</tr>')

            html_parts.append('</tbody></table>')
            html_parts.append('</div>')

        html_parts.append('</div>')
        self.analysis_html = "".join(html_parts)
