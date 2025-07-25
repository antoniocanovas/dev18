# Changelog

## [18.0.1.0.0] - 2025-01-27

### 🎯 Compatible con Odoo 18

#### Añadido
- Campo `variant_selection_mode` en product.template con opciones:
  - Product Configurator (modo por defecto)
  - Order Grid Entry (matriz siempre)
  - Allow Toggle (permite elegir)
  
- Wizard `variant.selector.wizard` para selección de formato

- JavaScript moderno compatible con OWL y Odoo 18

- Vistas heredadas usando nueva sintaxis (sin attrs/states)

- Sistema de permisos para el wizard

- Fallbacks inteligentes para diferentes configuraciones

- Documentación completa y README actualizado

#### Corregido
- ❌ **Eliminados attrs/states** (deprecated desde Odoo 17)
- ✅ **Nueva sintaxis**: `invisible="condition"` en lugar de `attrs="{'invisible': [...]}"` 
- ✅ **JavaScript OWL**: Compatible con componentes nativos de Odoo 18
- ✅ **XPath corregidos**: Sin dependencias de páginas específicas que pueden no existir
- ✅ **Bootstrap 5**: Estilos actualizados para nueva versión
- ✅ **Dependencias mínimas**: Solo módulos core (sale, product)

#### Características Técnicas
- Compatible con Odoo 18.0
- JavaScript ES6+ con imports/exports modernos
- CSS con variables CSS nativas
- Gestión de errores mejorada
- Fallbacks automáticos si faltan módulos opcionales

#### Estructura Mejorada
- Modelos Python simplificados
- Vistas XML optimizadas
- JavaScript modular y mantenible
- Sin dependencias externas

### Dependencias
- sale (core)
- product (core)

### Notas de Migración desde versiones anteriores
- Los attrs han sido reemplazados por sintaxis directa
- El JavaScript usa la nueva arquitectura OWL
- Las vistas son más robustas y compatibles
- Se eliminaron dependencias opcionales problemáticas

### Pruebas
- ✅ Instalación en Odoo 18.0
- ✅ Funcionamiento sin módulos adicionales
- ✅ Compatibilidad con variantes estándar
- ✅ Interfaz responsive y moderna
- ✅ Wizard de selección funcional

### Próximas mejoras planificadas
- Recordar última selección del usuario
- Configuración por usuario/grupo
- Atajos de teclado
- Integración con eCommerce
- Modo automático inteligente basado en número de variantes
