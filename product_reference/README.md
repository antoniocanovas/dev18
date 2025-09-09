# Product Reference Module

Módulo de Odoo 18 para gestión de referencias de productos con compatibilidades simétricas.

## Características

- **Referencias de Producto**: Gestión de referencias con nombre único y descripción
- **Compatibilidades Simétricas**: Si A es compatible con B, automáticamente B es compatible con A
- **Wizard de Gestión**: Interface intuitiva para gestionar compatibilidades con tres modos:
  - **Reemplazar**: Sustituye todas las compatibilidades existentes
  - **Añadir**: Agrega nuevas compatibilidades a las existentes
  - **Eliminar**: Quita compatibilidades específicas
- **Vista Previa**: Previsualiza los cambios antes de aplicarlos
- **Contadores**: Muestra el número de compatibilidades por referencia

## Estructura del Módulo

```
product_reference/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_reference.py
│   └── product_reference_compatibility.py
├── wizards/
│   ├── __init__.py
│   └── product_reference_compatibility_wizard.py
├── views/
│   ├── product_reference_views.xml
│   └── product_reference_compatibility_wizard_views.xml
├── security/
│   └── ir.model.access.csv
└── README.md
```

## Modelos

### ProductReference (`product.reference`)
- **name**: Nombre único de la referencia
- **description**: Descripción detallada
- **active**: Estado activo/archivado
- **compatibility_ids**: Compatibilidades directas (One2many)
- **all_compatible_ids**: Todas las compatibilidades (computado)
- **compatible_count**: Contador de compatibilidades

### ProductReferenceCompatibility (`product.reference.compatibility`)
- **reference_id**: Referencia principal
- **compatible_id**: Referencia compatible
- **notes**: Notas adicionales
- **active**: Estado activo/inactivo

### ProductReferenceCompatibilityWizard (`product.reference.compatibility.wizard`)
- **reference_id**: Referencia a gestionar
- **current_compatible_ids**: Compatibilidades actuales (solo lectura)
- **new_compatible_ids**: Referencias a seleccionar
- **mode**: Modo de operación (replace/add/remove)

## Uso

1. **Crear Referencias**: Ir a "Referencias de Producto" > "Referencias"
2. **Gestionar Compatibilidades**: Desde una referencia, clic en "Gestionar Compatibilidades"
3. **Seleccionar Modo**: Elegir entre Reemplazar, Añadir o Eliminar
4. **Vista Previa**: Opcionalmente previsualizar cambios
5. **Aplicar**: Confirmar los cambios

## Características Técnicas

- **Relaciones Simétricas**: Se mantienen automáticamente en `create()` y `unlink()`
- **Validaciones**: Evita auto-compatibilidades y duplicados
- **Performance**: Campos computados con dependencias optimizadas
- **UX**: Interface intuitiva con wizard modal y notificaciones

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo 18
2. Actualizar lista de aplicaciones
3. Instalar "Product Reference"

## Dependencias

- `base` (módulo base de Odoo)

## Versión

- **Odoo**: 18.0
- **Módulo**: 1.0.0
- **Licencia**: LGPL-3
