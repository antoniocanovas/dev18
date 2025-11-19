from odoo import fields, models

class ShoesAnalysisExport(models.TransientModel): # Usamos TransientModel, que es lo correcto para datos temporales de exportación
    _name = 'shoes.analysis.export'
    _description = 'Líneas de Datos Genéricas para Exportación de Análisis'

    analysis_id = fields.Many2one('shoes.analysis', 'Análisis', ondelete='set null')
    
    # Campos de Agrupación
    partner_id = fields.Many2one('res.partner', 'Cliente', ondelete='set null')
    referrer_id = fields.Many2one('res.users', 'Representante', ondelete='set null')
    country_id = fields.Many2one('res.country', 'País', ondelete='set null')
    manufacturer_id = fields.Many2one('res.partner', 'Fabricante', ondelete='set null') # Asumiendo res.partner para fabricante
    sale_type_id = fields.Many2one('sale.order.type', 'Timbrado', ondelete='set null')
    last_id = fields.Many2one('shoes.last', 'Horma', ondelete='set null')
    brand_name = fields.Char('Marca')
    
    # Campos de Datos
    campaign_id = fields.Many2one('project.project', 'Campaña', ondelete='set null')
    total_pairs = fields.Integer('Pares Pedidos')
    net_pairs = fields.Integer('Pares Netos')
    cancelled_pairs = fields.Integer('Pares Anulados')
    net_sales = fields.Float('Ventas Netas')
    
    # Campos Específicos (pueden estar vacíos)
    product_tmpl_id = fields.Many2one('product.template', 'Producto', ondelete='set null') # Para ranking de productos
    product_material_id = fields.Many2one('shoes.model.material', 'Material', ondelete='set null') # Nuevo campo para el código de producto
    ranking_name = fields.Char('Nombre') # Para ranking de productos
    ranking_value = fields.Integer('Posición') # Para ranking de productos
    product_ranking = fields.Integer('Ranking Producto')
    color_value_id = fields.Many2one('product.attribute.value', 'Color', ondelete='set null')
    sold_pairs = fields.Integer('Vendido')
    produced_pairs = fields.Integer('En Producción')
    estimated_stock = fields.Integer('Stock Estimado')
