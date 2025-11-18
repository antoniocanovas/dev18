from odoo import fields, models

class ShoesAnalysisExport(models.TransientModel): # Usamos TransientModel, que es lo correcto para datos temporales de exportación
    _name = 'shoes.analysis.export'
    _description = 'Líneas de Datos Genéricas para Exportación de Análisis'

    analysis_id = fields.Many2one('shoes.analysis', 'Análisis')
    
    # Campos de Agrupación
    partner_id = fields.Many2one('res.partner', 'Cliente')
    salesman_id = fields.Many2one('res.users', 'Representante')
    country_id = fields.Many2one('res.country', 'País')
    manufacturer_id = fields.Many2one('res.partner', 'Fabricante') # Asumiendo res.partner para fabricante
    sale_type_id = fields.Many2one('sale.order.type', 'Timbrado')
    last_id = fields.Many2one('shoes.last', 'Horma')
    
    # Campos de Datos
    campaign_id = fields.Many2one('project.project', 'Campaña')
    total_pairs = fields.Integer('Pares Pedidos')
    net_pairs = fields.Integer('Pares Netos')
    cancelled_pairs = fields.Integer('Pares Anulados')
    net_sales = fields.Float('Ventas Netas')
    
    # Campos Específicos (pueden estar vacíos)
    product_tmpl_id = fields.Many2one('product.template', 'Producto') # Para ranking de productos
    product_material_id = fields.Many2one('shoes.model.material', 'Artículo') # Nuevo campo para el código de producto
    ranking_name = fields.Char('Nombre Ranking') # Para ranking de productos
    ranking_value = fields.Integer('Valor Ranking') # Para ranking de productos
    
    # Campo de color (Many2one)
    color_value_id = fields.Many2one('product.attribute.value', 'Color') 
    
    update_date = fields.Datetime('Fecha Actualización')
