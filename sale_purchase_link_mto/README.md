# Sale Purchase Link MTO Enhancement - Backend Only

Este módulo proporciona **funcionalidad BACKEND** para vincular líneas de venta con líneas de compra en procesos Make-to-Order (MTO) estándar con purchase_stock.

## Problema Resuelto

En Odoo estándar, el campo `sale_line_id` solo se rellena en:
- ✅ Servicios con "Subcontract Service" (módulo `sale_purchase`)
- ✅ Dropshipping directo
- ❌ **MTO estándar con purchase_stock** ← Este módulo lo soluciona

## Funcionalidades Backend

### ✨ **Vinculación Automática**
- Propaga `sale_line_id` desde `stock.move` a `procurement.group`
- Mantiene la relación a través de `stock.rule`
- Compatible con rutas MTO + Buy

### 📊 **Campos Disponibles Programáticamente**
- **`sale_line_id`**: Vincula a la línea de venta original (`sale.order.line`)
- **`customer_id`**: Cliente final calculado desde `sale_line_id.order_id.partner_id`

### 🔄 **Flujo Completo**
```
Sale Order → Stock Move → Procurement → Stock Rule → Purchase Order
     ↓           ↓            ↓            ↓            ↓
sale_line_id propagado automáticamente en todo el flujo + customer_id calculado
```

### 📈 **Beneficios**
- **Trazabilidad completa:** De venta a compra (programáticamente)
- **Análisis de márgenes:** Vinculación directa SO-PO
- **Reportes mejorados:** Origen de compras identificable
- **Auditoría:** Seguimiento completo de transacciones

## Instalación

1. **Colocar el módulo:**
   ```bash
   cp -r sale_purchase_link_mto /path/to/odoo/addons/
   ```

2. **Reiniciar Odoo y actualizar lista de apps**

3. **Instalar dependencias** (si no están):
   - `sale_stock`
   - `purchase_stock` 
   - `sale_purchase_stock`

4. **Instalar el módulo:**
   ```
   Apps → Search "Sale Purchase Line Link MTO" → Install
   ```

## Configuración del Producto

Para que funcione, el producto debe tener:

```python
# Rutas requeridas:
- ✅ Make To Order (MTO)
- ✅ Buy (Purchase route)

# Proveedor configurado:
- ✅ Al menos un vendor en la pestaña "Purchase"
```
