# CHANGELOG - Sale Product Matrix Configurator

## v1.0.3 - Corrección definitiva (ACTUAL)

### ✅ **PROBLEMA RESUELTO**
Los valores de atributos personalizados de texto libre no se guardaban en `product_custom_attribute_value_ids` después de usar el configurador de productos.

### 🔧 **CAMBIOS IMPLEMENTADOS**

#### 1. **JavaScript completamente reescrito** (`static/src/js/sale_product_field_configurator.js`)
- **IMPORTACIÓN CORRECTA**: `import { getSelectedCustomPtav } from "@sale/js/sale_utils"`
- **MÉTODO `_applyProduct`**: Implementación idéntica al core de Odoo
- **PATRÓN ESTÁNDAR**: Usa `getSelectedCustomPtav(ptal)` + `ptal.customValue`
- **COMANDOS X2MANY**: `x2ManyCommands.set([])` + `x2ManyCommands.create()`

```javascript
// CÓDIGO CLAVE - Patrón del core de Odoo
for (const ptal of product.attribute_lines) {
    const selectedCustomPTAV = getSelectedCustomPtav(ptal);
    if (selectedCustomPTAV) {
        customAttributesCommands.push(
            x2ManyCommands.create(undefined, {
                custom_product_template_attribute_value_id: [selectedCustomPTAV.id, "we don't care"],
                custom_value: ptal.customValue,  // ← PRESERVA TEXTO LIBRE
            })
        );
    }
}
```

#### 2. **Modelo Python simplificado** (`models/sale_order_line.py`)
- **SOLO CAMPO ESENCIAL**: `sale_order_line_id` en `ProductAttributeCustomValue`
- **SIN TOCAR CORE**: Mantiene `_compute_name` original
- **COMPATIBILIDAD TOTAL**: Con estándar Odoo 18

```python
class ProductAttributeCustomValue(models.Model):
    _inherit = 'product.attribute.custom.value'
    
    # Solo el campo requerido por inverse_name
    sale_order_line_id = fields.Many2one(
        'sale.order.line', 
        string="Sale Order Line", 
        ondelete='cascade'
    )
```

#### 3. **Manifest actualizado** (`__manifest__.py`)
- **VERSIÓN**: 1.0.3
- **DEPENDENCIAS**: `'sale', 'sale_product_matrix', 'product'`
- **DESCRIPCIÓN**: Actualizada con correcciones

#### 4. **Tests incluidos** (`tests/`)
- `test_custom_attributes.py`: Tests unitarios
- `verify_installation.py`: Script de verificación completo

### 🎯 **RESULTADO ESPERADO**

#### ✅ **ANTES (Fallaba)**:
```
Usuario rellena campo texto libre: "Mi nombre es Juan"
→ product_custom_attribute_value_ids: [] (vacío)
→ Descripción: "Camiseta Personalizada" (sin custom value)
```

#### ✅ **DESPUÉS (Funciona)**:
```
Usuario rellena campo texto libre: "Mi nombre es Juan"  
→ product_custom_attribute_value_ids: [record con custom_value="Mi nombre es Juan"]
→ Descripción: "Camiseta Personalizada\nTexto personalizado: Mi nombre es Juan"
```

### 🧪 **VERIFICACIÓN**

#### Desde shell de Odoo:
```python
# Ejecutar script de verificación
exec(open('/path/to/verify_installation.py').read())

# Verificación manual
lines = env['sale.order.line'].search([('product_custom_attribute_value_ids', '!=', False)])
for line in lines:
    print(f"Línea {line.id}: {line.name}")
    for custom in line.product_custom_attribute_value_ids:
        print(f"  - {custom.name}: '{custom.custom_value}'")
```

### 📁 **ARCHIVOS MODIFICADOS**

```
sale_product_matrix_configurator/
├── __manifest__.py                          # ✅ v1.0.3 + dependencia 'product'
├── models/sale_order_line.py               # ✅ Simplificado, solo sale_order_line_id
├── static/src/js/sale_product_field_configurator.js  # ✅ Reescrito con patrón core
├── views/sale_order_views.xml              # ✅ Vistas correctas
├── tests/
│   ├── __init__.py                         # ✅ Tests unitarios
│   └── test_custom_attributes.py           # ✅ Tests de custom attributes
├── verify_installation.py                  # ✅ Script de verificación
├── CHANGELOG.md                            # ✅ Este archivo
└── README.md                               # ✅ Documentación completa
```

---

## Versiones anteriores

### v1.0.2 - Corrección JavaScript (Superseded)
- Intentó corregir JavaScript pero no siguió el patrón del core
- Problema: Uso incorrecto de `ptav.is_custom` y `attrLine.custom_value`

### v1.0.1 - Primera corrección (Superseded)  
- Intentó extender `_compute_name`
- Problema: Interfería con el core de Odoo

### v1.0.0 - Versión inicial
- Funcionalidad básica del selector de configurador
- Problema: No preservaba custom attributes

---

## 🎯 **CONSOLIDACIÓN COMPLETADA**

**Todos los cambios han sido consolidados en el módulo base `sale_product_matrix_configurator`. El módulo ahora sigue exactamente el patrón del core de Odoo y debería preservar correctamente todos los valores de atributos personalizados de texto libre.**

**Para aplicar**: 
1. `./odoo-bin -u sale_product_matrix_configurator`
2. Ejecutar `verify_installation.py` para confirmar funcionamiento
3. Probar con producto que tenga atributo de tipo "text"
