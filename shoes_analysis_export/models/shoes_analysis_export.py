from odoo import fields, models

class ShoesAnalysisExport(models.TransientModel):
    _name = 'shoes.analysis.export'
    _description = 'Líneas de Datos Genéricas para Exportación de Análisis'

    analysis_id = fields.Many2one('shoes.analysis', 'Análisis')
    
    # Campos de Agrupación
    partner_id = fields.Many2one('res.partner', 'Cliente')
    referrer_id = fields.Many2one('res.users', 'Representante')
    country_id = fields.Many2one('res.country', 'País')
    manufacturer_id = fields.Many2one('res.partner', 'Fabricante')
    sale_type_id = fields.Many2one('sale.order.type', 'Timbrado')
    last_id = fields.Many2one('shoes.last', 'Horma')
    brand_name = fields.Char('Marca')
    
    # Campos de Datos
    campaign_id = fields.Many2one('project.project', 'Campaña')
    total_pairs = fields.Integer('Pares Pedidos')
    net_pairs = fields.Integer('Pares Netos')
    cancelled_pairs = fields.Integer('Pares Anulados')
    net_sales = fields.Float('Ventas Netas')
    
    # Campos Específicos (pueden estar vacíos)
    product_tmpl_id = fields.Many2one('product.template', 'Producto')
    product_material_id = fields.Many2one('shoes.model.material', 'Material')
    ranking_name = fields.Char('Nombre')
    ranking_value = fields.Integer('Posición')
    product_ranking = fields.Integer('Ranking Producto')
    color_value_id = fields.Many2one('product.attribute.value', 'Color')
    sold_pairs = fields.Integer('Vendido')
    produced_pairs = fields.Integer('En Producción')
    estimated_stock = fields.Integer('Stock Estimado')
