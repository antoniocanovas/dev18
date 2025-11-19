from odoo import models, fields, api
from odoo.exceptions import UserError

class ShoesAnalysis(models.Model):
    _inherit = 'shoes.analysis'

    def action_export_to_spreadsheet(self):
        """
        Dispatcher para abrir la vista de lista del modelo transitorio de exportación
        correcto según el tipo de informe actual.
        """
        self.ensure_one()
        if not self.analysis_html:
            return False
        
        # Mapeo de tipos de informe a sus vistas de lista y métodos de parseo
        export_config = {
            'salesman_sales_delivery': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_salesman_delivery_list_view',
                'parser': '_parse_salesman_sales_delivery_data',
            },
            'salesman_country': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_salesman_country_list_view',
                'parser': '_parse_salesman_country_data',
            },
            'manufacturer_sales': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_manufacturer_sales_list_view',
                'parser': '_parse_manufacturer_sales_data',
            },
            'sales_by_country': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_sales_by_country_list_view',
                'parser': '_parse_sales_by_country_data',
            },
            'sales_by_shipping_mark': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_sales_by_shipping_mark_list_view',
                'parser': '_parse_sales_by_shipping_mark_data',
            },
            'product_ranking': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_product_ranking_list_view',
                'parser': '_parse_product_ranking_data',
            },
            'last_ranking': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_last_ranking_list_view',
                'parser': '_parse_last_ranking_data',
            },
            'campaign_product_ranking': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_campaign_product_ranking_list_view',
                'parser': '_parse_campaign_product_ranking_data',
            },
            'campaign_last_ranking': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_campaign_last_ranking_list_view',
                'parser': '_parse_campaign_last_ranking_data',
            },
            'salesman_model': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_salesman_model_list_view',
                'parser': '_parse_salesman_model_data',
            },
            'customer_comparison': {
                'view_id': 'shoes_analysis_export.shoes_analysis_export_customer_comparison_list_view',
                'parser': '_parse_customer_comparison_data',
            },
        }
        
        config = export_config.get(self.type)
        if not config:
            raise UserError(f"La exportación a hoja de cálculo no está implementada para el tipo de informe: {self.type}")

        export_model = self.env['shoes.analysis.export']
        
        # Borrar registros antiguos para este análisis
        records_to_delete = export_model.search([('analysis_id', '=', self.id)])
        if records_to_delete:
            records_to_delete.write({
                'analysis_id': False,
                'partner_id': False,
                'referrer_id': False,
                'country_id': False,
                'manufacturer_id': False,
                'sale_type_id': False,
                'last_id': False,
                'campaign_id': False,
                'product_tmpl_id': False,
                'product_material_id': False,
                'color_value_id': False,
            })
            records_to_delete.unlink()

        parser_method = getattr(self, config['parser'])
        
        # Crear los registros transitorios
        lines_to_create = parser_method(self.data)
        records = export_model.create(lines_to_create)

        # Devolver la acción para abrir la vista de lista
        return {
            'name': f'Datos de Análisis: {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': export_model._name, # Usar el nombre del modelo transitorio único
            'view_mode': 'list',
            'views': [(self.env.ref(config['view_id']).id, 'list')],
            'domain': [('id', 'in', records.ids)],
            'target': 'current',
        }

    def _parse_salesman_sales_delivery_data(self, json_data):
        """ Parsea los datos JSON para el informe 'salesman_sales_delivery'. """
        lines_to_create = []
        for salesman_data in json_data.get('detalle_representantes', []):
            for campaign_data in salesman_data.get('campanias', []):
                lines_to_create.append({
                    'referrer_id': self.env['res.users'].search([('name', '=', salesman_data.get('representante'))], limit=1).id,
                    'campaign_id': self.shoes_campaign_id.id,
                    'net_pairs': campaign_data.get('netos'),
                    'net_sales': campaign_data.get('total_vendido'),
                    'cancelled_pairs': campaign_data.get('total_cancelados'),
                    'total_pairs': campaign_data.get('total_vendidos'),
                    'analysis_id': self.id, # Enlazar con el análisis original
                })
        return lines_to_create

    def _parse_salesman_country_data(self, json_data):
        """ Parsea los datos JSON para el informe 'salesman_country'. """
        lines_to_create = []
        for salesman_data in json_data: # La estructura JSON es una lista de representantes
            referrer_id = self.env['res.users'].search([('name', '=', salesman_data.get('salesman_name'))], limit=1).id
            for country_data in salesman_data.get('countries', []):
                country_id = self.env['res.country'].search([('name', '=', country_data.get('country_name'))], limit=1).id
                for campaign_data in country_data.get('campaigns', []):
                    lines_to_create.append({
                        'referrer_id': referrer_id,
                        'country_id': country_id,
                        'campaign_id': self.shoes_campaign_id.id,
                        'net_pairs': campaign_data.get('net_pairs'),
                        'net_sales': campaign_data.get('net_sales'),
                        'total_pairs': campaign_data.get('total_pairs'),
                        'cancelled_pairs': campaign_data.get('cancelled_pairs'),
                        'analysis_id': self.id, # Enlazar con el análisis original
                    })
        return lines_to_create

    def _parse_manufacturer_sales_data(self, json_data):
        """ Parsea los datos JSON para el informe 'manufacturer_sales'. """
        lines_to_create = []
        for manufacturer_data in json_data: # La estructura JSON es una lista de fabricantes
            manufacturer_id = self.env['res.partner'].search([('name', '=', manufacturer_data.get('manufacturer_name'))], limit=1).id
            for campaign_data in manufacturer_data.get('campaigns', []):
                lines_to_create.append({
                    'manufacturer_id': manufacturer_id,
                    'campaign_id': self.shoes_campaign_id.id,
                    'net_pairs': campaign_data.get('net_pairs'),
                    'net_sales': campaign_data.get('net_sales'),
                    'analysis_id': self.id, # Enlazar con el análisis original
                })
        return lines_to_create

    def _parse_sales_by_country_data(self, json_data):
        """ Parsea los datos JSON para el informe 'sales_by_country'. """
        lines_to_create = []
        for country_data in json_data: # La estructura JSON es una lista de países
            country_id = self.env['res.country'].search([('name', '=', country_data.get('country_name'))], limit=1).id
            for campaign_data in country_data.get('campaigns', []):
                lines_to_create.append({
                    'country_id': country_id,
                    'campaign_id': self.shoes_campaign_id.id,
                    'net_pairs': campaign_data.get('net_pairs'),
                    'net_sales': campaign_data.get('net_sales'),
                    'analysis_id': self.id, # Enlazar con el análisis original
                })
        return lines_to_create

    def _parse_sales_by_shipping_mark_data(self, json_data):
        """ Parsea los datos JSON para el informe 'sales_by_shipping_mark'. """
        lines_to_create = []
        for mark_data in json_data: # La estructura JSON es una lista de timbrados
            sale_type_id = self.env['sale.order.type'].search([('name', '=', mark_data.get('shipping_mark_name'))], limit=1).id
            for campaign_data in mark_data.get('campaigns', []):
                lines_to_create.append({
                    'sale_type_id': sale_type_id,
                    'campaign_id': self.shoes_campaign_id.id,
                    'net_pairs': campaign_data.get('net_pairs'),
                    'net_sales': campaign_data.get('net_sales'),
                    'analysis_id': self.id, # Enlazar con el análisis original
                })
        return lines_to_create

    def _parse_product_ranking_data(self, json_data):
        """ Parsea los datos JSON para el informe 'product_ranking'. """
        lines_to_create = []
        for item in json_data:
            lines_to_create.append({
                'ranking_name': item.get('name'),
                'ranking_value': item.get('ranking'),
                'product_tmpl_id': item.get('product_tmpl_id')[0] if item.get('product_tmpl_id') else False,
                'campaign_id': self.shoes_campaign_id.id,
                'net_pairs': item.get('pairs_count_net'),
                'net_sales': item.get('sale_net_amount'),
                'total_pairs': item.get('pairs_count_sale'),
                'cancelled_pairs': item.get('pairs_count_cancel'),
                'analysis_id': self.id,
            })
        return lines_to_create

    def _parse_last_ranking_data(self, json_data):
        """ Parsea los datos JSON para el informe 'last_ranking'. """
        lines_to_create = []
        for item in json_data:
            lines_to_create.append({
                'ranking_name': item.get('name'),
                'ranking_value': item.get('ranking'),
                'last_id': item.get('shoes_last_id')[0] if item.get('shoes_last_id') else False,
                'campaign_id': self.shoes_campaign_id.id,
                'net_pairs': item.get('pairs_count_net'),
                'net_sales': item.get('sale_net_amount'),
                'total_pairs': item.get('pairs_count_sale'),
                'cancelled_pairs': item.get('pairs_count_cancel'),
                'analysis_id': self.id,
            })
        return lines_to_create

    def _parse_campaign_product_ranking_data(self, json_data):
        """
        Parsea los datos JSON para el informe 'campaign_product_ranking'.
        """
        lines_to_create = []
        for item in json_data:
            for color in item.get('colors', []):
                lines_to_create.append({
                    'ranking_value': item.get('ranking'),
                    'ranking_name': item.get('name'),
                    'product_material_id': item.get('shoes_model_material_id')[0] if item.get('shoes_model_material_id') else False,
                    'color_value_id': self.env['product.attribute.value'].search([('name', '=', color.get('color_name'))], limit=1).id,
                    'sold_pairs': color.get('sold'),
                    'produced_pairs': color.get('produced'),
                    'estimated_stock': color.get('stock'),
                    'analysis_id': self.id,
                    'campaign_id': self.shoes_campaign_id.id,
                })
        return lines_to_create

    def _parse_campaign_last_ranking_data(self, json_data):
        """
        Parsea los datos JSON para el informe 'campaign_last_ranking'.
        """
        lines_to_create = []
        for item in json_data:
            for product in item.get('products', []):
                for color in product.get('colors', []):
                    lines_to_create.append({
                        'last_id': item.get('shoes_last_id')[0] if item.get('shoes_last_id') else False,
                        'product_tmpl_id': product.get('product_tmpl_id')[0] if product.get('product_tmpl_id') else False,
                        'ranking_value': product.get('ranking'),
                        'ranking_name': product.get('name'),
                        'product_material_id': product.get('shoes_model_material_id')[0] if product.get('shoes_model_material_id') else False,
                        'color_value_id': self.env['product.attribute.value'].search([('name', '=', color.get('color_name'))], limit=1).id,
                        'sold_pairs': color.get('sold'),
                        'produced_pairs': color.get('produced'),
                        'estimated_stock': color.get('stock'),
                        'analysis_id': self.id,
                        'campaign_id': self.shoes_campaign_id.id,
                    })
        return lines_to_create

    def _parse_salesman_model_data(self, json_data):
        """
        Parsea los datos JSON para el informe 'salesman_model'.
        """
        lines_to_create = []
        for item in json_data:
            lines_to_create.append({
                'referrer_id': item.get('referrer_id'),
                'ranking_value': item.get('ranking_value'),
                'product_material_id': item.get('shoes_model_material_id'),
                'ranking_name': item.get('product_name'),
                'total_pairs': item.get('pedidos'),
                'cancelled_pairs': item.get('anulados'),
                'net_pairs': item.get('venta_neta'),
                'analysis_id': self.id,
                'campaign_id': self.shoes_campaign_id.id,
            })
        return lines_to_create

    def _parse_customer_comparison_data(self, json_data):
        """
        Parsea los datos JSON para el informe 'customer_comparison'.
        """
        lines_to_create = []
        for partner_data in json_data:
            for brand_data in partner_data.get('brands', []):
                for campaign_data in brand_data.get('campaigns', []):
                    lines_to_create.append({
                        'partner_id': partner_data.get('partner_id'),
                        'brand_name': brand_data.get('brand_name'),
                        'campaign_id': campaign_data.get('campaign_id'),
                        'net_pairs': campaign_data.get('net_pairs'),
                        'net_sales': campaign_data.get('net_sales'),
                        'analysis_id': self.id,
                    })
        return lines_to_create
