# Copyright 2025 Serincloud SL - Ingenieriacloud.com
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, fields, models, _
from odoo.tools import date_utils
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class ShoesSalesStatisticsReport(models.AbstractModel):
    _name = 'shoes.sales.statistics.report'
    _description = 'Shoes Sales Statistics Report Handler'

    def _get_columns_name(self, options):
        return [
            {'name': _('Size'), 'class': 'text-start', 'style': 'white-space:nowrap;'},
            {'name': _('Sold'), 'class': 'number', 'style': 'white-space:nowrap;'},
            {'name': _('Delivered'), 'class': 'number', 'style': 'white-space:nowrap;'},
            {'name': _('Invoiced'), 'class': 'number', 'style': 'white-space:nowrap;'},
        ]

    def _get_report_name(self):
        return _("Shoes Sales Statistics")

    def _get_lines(self, options, line_id=None):
        lines = []
        
        # Get date range from options
        date_from = options.get('date', {}).get('date_from')
        date_to = options.get('date', {}).get('date_to')
        
        if not date_from or not date_to:
            return lines
        
        # Build domain for analysis records
        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', 'in', ['sale', 'done']),
            ('assortment_attribute_id', '=', False),  # Only pairs
        ]
        
        # Add brand filter if selected
        if options.get('brand_ids'):
            domain.append(('brand_id', 'in', options['brand_ids']))
            
        # Add team filter if selected  
        if options.get('team_ids'):
            domain.append(('team_id', 'in', options['team_ids']))
            
        # Add salesman filter if selected
        if options.get('salesman_ids'):
            domain.append(('salesman_id', 'in', options['salesman_ids']))

        # Get analysis records
        analysis_records = self.env['shoes.dealer.analysis'].search(domain)
        
        if not analysis_records:
            return lines

        # Group by product template model
        models_data = {}
        for record in analysis_records:
            model_id = record.product_tmpl_model_id.id if record.product_tmpl_model_id else False
            model_name = record.product_tmpl_model_id.name if record.product_tmpl_model_id else _('Undefined Model')
            
            if model_id not in models_data:
                models_data[model_id] = {
                    'name': model_name,
                    'model_id': model_id,
                    'colors': {},
                    'total_sold': 0,
                    'total_delivered': 0,
                    'total_invoiced': 0,
                }
            
            # Group by color within model
            color_id = record.color_value_id.id if record.color_value_id else False
            color_name = record.color_value_id.name if record.color_value_id else _('No Color')
            
            if color_id not in models_data[model_id]['colors']:
                models_data[model_id]['colors'][color_id] = {
                    'name': color_name,
                    'color_id': color_id,
                    'sizes': {},
                    'total_sold': 0,
                    'total_delivered': 0,
                    'total_invoiced': 0,
                }
            
            # Group by size within color
            size_id = record.size_value_id.id if record.size_value_id else False
            size_name = record.size_value_id.name if record.size_value_id else _('No Size')
            
            if size_id not in models_data[model_id]['colors'][color_id]['sizes']:
                models_data[model_id]['colors'][color_id]['sizes'][size_id] = {
                    'name': size_name,
                    'sold': 0,
                    'delivered': 0,
                    'invoiced': 0,
                }
            
            # Accumulate quantities
            qty_multiplier = record.bom_qty or 1.0
            sold_qty = (record.sale_qty or 0) * qty_multiplier
            delivered_qty = (record.delivery_qty or 0) * qty_multiplier  
            invoiced_qty = (record.invoice_qty or 0) * qty_multiplier
            
            models_data[model_id]['colors'][color_id]['sizes'][size_id]['sold'] += sold_qty
            models_data[model_id]['colors'][color_id]['sizes'][size_id]['delivered'] += delivered_qty
            models_data[model_id]['colors'][color_id]['sizes'][size_id]['invoiced'] += invoiced_qty
            
            models_data[model_id]['colors'][color_id]['total_sold'] += sold_qty
            models_data[model_id]['colors'][color_id]['total_delivered'] += delivered_qty
            models_data[model_id]['colors'][color_id]['total_invoiced'] += invoiced_qty
            
            models_data[model_id]['total_sold'] += sold_qty
            models_data[model_id]['total_delivered'] += delivered_qty
            models_data[model_id]['total_invoiced'] += invoiced_qty

        # Sort models by total sold (descending)
        sorted_models = sorted(models_data.values(), key=lambda x: x['total_sold'], reverse=True)
        
        # Build report lines
        for model_data in sorted_models:
            # Model header line
            model_line = {
                'id': f"model_{model_data['model_id']}",
                'name': model_data['name'],
                'level': 1,
                'unfoldable': True,
                'unfolded': True,
                'columns': [
                    {'name': ''},
                    {'name': self._format_value(model_data['total_sold'])},
                    {'name': self._format_value(model_data['total_delivered'])},
                    {'name': self._format_value(model_data['total_invoiced'])},
                ],
                'class': 'o_account_report_line_clickable',
            }
            lines.append(model_line)
            
            # Sort colors by total sold (descending)
            sorted_colors = sorted(model_data['colors'].values(), key=lambda x: x['total_sold'], reverse=True)
            
            for color_data in sorted_colors:
                # Color header line
                color_line = {
                    'id': f"color_{color_data['color_id']}_{model_data['model_id']}",
                    'name': f"  {color_data['name']}",
                    'level': 2,
                    'unfoldable': True,
                    'unfolded': True,
                    'columns': [
                        {'name': ''},
                        {'name': self._format_value(color_data['total_sold'])},
                        {'name': self._format_value(color_data['total_delivered'])},
                        {'name': self._format_value(color_data['total_invoiced'])},
                    ],
                    'class': 'o_account_report_line_clickable',
                }
                lines.append(color_line)
                
                # Sort sizes by sold quantity (descending)
                sorted_sizes = sorted(color_data['sizes'].values(), key=lambda x: x['sold'], reverse=True)
                
                for size_data in sorted_sizes:
                    # Size detail line
                    size_line = {
                        'id': f"size_{size_data['name']}_{color_data['color_id']}_{model_data['model_id']}",
                        'name': f"    {size_data['name']}",
                        'level': 3,
                        'unfoldable': False,
                        'columns': [
                            {'name': size_data['name']},
                            {'name': self._format_value(size_data['sold'])},
                            {'name': self._format_value(size_data['delivered'])},
                            {'name': self._format_value(size_data['invoiced'])},
                        ],
                    }
                    lines.append(size_line)

        return lines

    def _format_value(self, value):
        """Format numerical values for display"""
        if not value:
            return '0'
        return f"{value:,.0f}"

    @api.model
    def get_filter_data(self):
        """Return data for custom filters"""
        brands = self.env['product.brand'].search([])
        teams = self.env['crm.team'].search([])
        salesmen = self.env['res.users'].search([('share', '=', False)])
        
        return {
            'brands': [{'id': b.id, 'name': b.name} for b in brands],
            'teams': [{'id': t.id, 'name': t.name} for t in teams],
            'salesmen': [{'id': s.id, 'name': s.name} for s in salesmen],
        }

    def get_html(self, options, line_id=None, additional_context=None):
        """Generate HTML for the report"""
        lines = self._get_lines(options, line_id)
        
        rcontext = {
            'report': self,
            'options': options,
            'lines': lines,
            'columns': self._get_columns_name(options),
            'report_name': self._get_report_name(),
        }
        
        if additional_context:
            rcontext.update(additional_context)
            
        render_template = 'account_reports.main_template'
        html = self.env['ir.ui.view']._render_template(render_template, rcontext)
        return html
        
    def get_xlsx(self, options, response=None):
        """Generate XLSX export"""
        # Basic XLSX implementation
        return self.env['account.report']._get_xlsx_data(options, self._get_lines(options))
