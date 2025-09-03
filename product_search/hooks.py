import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Hook ejecutado después de la instalación del módulo
    """
    _logger.info("=== Búsqueda Inteligente de Productos - Post Instalación ===")
    
    try:
        # Crear datos iniciales si es necesario
        with registry.cursor() as new_cr:
            env = registry.get(new_cr)
            
            # Verificar si hay productos en el sistema
            product_count = env['product.template'].search_count([('active', '=', True)])
            
            if product_count == 0:
                _logger.warning(
                    "⚠️  No se encontraron productos activos. "
                    "Considera crear productos de ejemplo para probar el módulo."
                )
            else:
                _logger.info(f"✅ Se encontraron {product_count} productos activos en el sistema.")
            
            # Crear configuración inicial si es necesario
            _create_initial_config(env)
            
            # Mensaje de bienvenida
            _logger.info("🎉 ¡Módulo de Búsqueda Inteligente instalado correctamente!")
            _logger.info("📖 Consulta la documentación en README.md para empezar.")
            
    except Exception as e:
        _logger.error(f"❌ Error durante la post-instalación: {e}")


def uninstall_hook(cr, registry):
    """
    Hook ejecutado antes de la desinstalación del módulo
    """
    _logger.info("=== Búsqueda Inteligente de Productos - Desinstalación ===")
    
    try:
        with registry.cursor() as new_cr:
            env = registry.get(new_cr)
            
            # Limpiar datos relacionados si es necesario
            _cleanup_module_data(env)
            
            _logger.info("🗑️ Módulo desinstalado correctamente.")
            _logger.info("📊 Los datos de búsqueda se mantienen para futuras reinstalaciones.")
            
    except Exception as e:
        _logger.error(f"❌ Error durante la desinstalación: {e}")


def _create_initial_config(env):
    """
    Crear configuración inicial del módulo
    """
    try:
        # Crear parámetros de configuración si no existen
        IrConfig = env['ir.config_parameter'].sudo()
        
        # Configuraciones por defecto
        default_configs = {
            'product_search.max_results': '50',
            'product_search.enable_learning': 'True',
            'product_search.interaction_threshold': '30',
            'product_search.cache_enabled': 'True',
            'product_search.debug_mode': 'False'
        }
        
        for key, value in default_configs.items():
            existing = IrConfig.search([('key', '=', key)])
            if not existing:
                IrConfig.create({
                    'key': key,
                    'value': value
                })
                _logger.info(f"⚙️  Configuración creada: {key} = {value}")
        
        _logger.info("✅ Configuración inicial completada.")
        
    except Exception as e:
        _logger.error(f"❌ Error creando configuración inicial: {e}")


def _cleanup_module_data(env):
    """
    Limpiar datos del módulo durante la desinstalación
    """
    try:
        # Opcional: limpiar datos temporales o caché
        # No eliminamos búsquedas guardadas para preservar historial
        
        # Limpiar configuraciones si se desea
        IrConfig = env['ir.config_parameter'].sudo()
        configs_to_remove = IrConfig.search([
            ('key', 'like', 'product_search.%')
        ])
        
        if configs_to_remove:
            # configs_to_remove.unlink()  # Comentado para preservar configuración
            _logger.info(f"🔧 Se encontraron {len(configs_to_remove)} configuraciones (preservadas).")
        
        _logger.info("🧹 Limpieza completada.")
        
    except Exception as e:
        _logger.error(f"❌ Error durante la limpieza: {e}")


def upgrade_module(cr, version):
    """
    Hook ejecutado durante actualizaciones del módulo
    """
    _logger.info(f"🔄 Actualizando Búsqueda Inteligente a versión {version}")
    
    try:
        # Lógica de migración según la versión
        if version.startswith('18.0.1.'):
            _logger.info("✅ Actualización a versión 18.0.1.x completada.")
            
    except Exception as e:
        _logger.error(f"❌ Error durante la actualización: {e}")
