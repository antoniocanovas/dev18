from odoo import api, fields, models
from odoo.osv import expression
import logging

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """
    Extiende 'product.product' para permitir una búsqueda flexible e independiente 
    del orden por nombre de plantilla y valores de atributo.
    """
    _inherit = "product.product"

    var_desc = fields.Text(
        string="Descripción de Variante para Búsqueda",
        compute="_compute_var_desc",
        store=True,
        help="Nombre de plantilla y valores de atributo concatenados para búsquedas flexibles.",
    )

    @api.depends(
        "product_template_attribute_value_ids.product_attribute_value_id.name",
        "product_tmpl_id.name",
    )
    def _compute_var_desc(self) -> None:
        """
        Calcula la descripción de búsqueda de la variante.
        """
        for product in self:
            desc_parts = []
            
            # Añadir nombre del template
            if product.product_tmpl_id.name:
                desc_parts.append(product.product_tmpl_id.name)
            
            # Añadir valores de atributos
            if product.product_template_attribute_value_ids:
                attribute_names = product.product_template_attribute_value_ids.mapped(
                    'product_attribute_value_id.name'
                )
                desc_parts.extend(attribute_names)
            
            # Unir todo
            product.var_desc = " ".join(filter(None, desc_parts))
            
            _logger.info(f"Producto {product.id} ({product.display_name}): var_desc = '{product.var_desc}'")

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """
        Búsqueda extendida con logging para debug
        """
        _logger.info(f"=== BÚSQUEDA INICIADA ===")
        _logger.info(f"Término: '{name}', Operator: {operator}, Limit: {limit}")
        _logger.info(f"Args: {args}")
        
        # Búsqueda estándar primero
        standard_results = super().name_search(name, args, operator, limit)
        _logger.info(f"Búsqueda estándar encontró: {len(standard_results)} resultados")
        
        # Si no hay término de búsqueda, retornar estándar
        if not name or not isinstance(name, str) or not name.strip():
            _logger.info("No hay término de búsqueda válido")
            return standard_results
        
        # Obtener términos de búsqueda
        search_terms = name.split()
        _logger.info(f"Términos de búsqueda: {search_terms}")
        
        # Si solo hay un término o ya tenemos suficientes resultados, no buscar más
        if len(search_terms) <= 1:
            _logger.info("Solo un término, usando búsqueda estándar")
            return standard_results
            
        if limit and len(standard_results) >= limit:
            _logger.info("Ya tenemos suficientes resultados")
            return standard_results
        
        # IDs ya encontrados
        found_ids = {result[0] for result in standard_results}
        _logger.info(f"IDs ya encontrados: {found_ids}")
        
        # Crear dominio para var_desc - CADA término debe estar presente
        var_desc_domain = []
        for term in search_terms:
            var_desc_domain.append(('var_desc', 'ilike', term))
        
        # Excluir productos ya encontrados
        if found_ids:
            var_desc_domain.append(('id', 'not in', list(found_ids)))
        
        # Añadir args originales
        if args:
            var_desc_domain.extend(args)
        
        _logger.info(f"Dominio var_desc: {var_desc_domain}")
        
        try:
            # Calcular límite restante
            remaining_limit = limit - len(standard_results) if limit else 100
            
            # Búsqueda adicional
            additional_products = self.search(var_desc_domain, limit=remaining_limit)
            _logger.info(f"Búsqueda adicional encontró: {len(additional_products)} productos")
            
            if additional_products:
                for prod in additional_products:
                    _logger.info(f"  - {prod.display_name} (var_desc: '{prod.var_desc}')")
            
            # Convertir a formato name_search
            additional_results = []
            for product in additional_products:
                additional_results.append((product.id, product.display_name))
            
            # Combinar resultados
            combined_results = standard_results + additional_results
            _logger.info(f"Total resultados combinados: {len(combined_results)}")
            
            return combined_results[:limit] if limit else combined_results
            
        except Exception as e:
            _logger.error(f"Error en búsqueda adicional: {e}")
            return standard_results
