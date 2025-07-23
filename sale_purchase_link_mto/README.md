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

## Uso Programático

### **Acceder a la vinculación desde código:**

```python
# Buscar líneas de compra vinculadas
po_lines = env['purchase.order.line'].search([
    ('sale_line_id', '!=', False)
])

for po_line in po_lines:
    # Acceder a la línea de venta original
    sale_line = po_line.sale_line_id
    sale_order = sale_line.order_id
    
    # Acceder al cliente final
    customer = po_line.customer_id
    
    print(f"PO: {po_line.order_id.name}")
    print(f"Generado desde SO: {sale_order.name}")
    print(f"Cliente final: {customer.name}")
    print(f"Producto: {po_line.product_id.name}")
    print("---")
```

### **Análisis de márgenes:**

```python
# Comparar precios de venta vs compra
po_lines_with_sale = env['purchase.order.line'].search([
    ('sale_line_id', '!=', False)
])

for po_line in po_lines_with_sale:
    sale_line = po_line.sale_line_id
    
    # Calcular margen
    sale_price = sale_line.price_subtotal
    purchase_price = po_line.price_subtotal
    margin = sale_price - purchase_price
    margin_pct = (margin / sale_price * 100) if sale_price else 0
    
    print(f"Cliente: {po_line.customer_id.name}")
    print(f"Producto: {po_line.product_id.name}")
    print(f"Venta: €{sale_price:.2f}")
    print(f"Compra: €{purchase_price:.2f}")
    print(f"Margen: €{margin:.2f} ({margin_pct:.1f}%)")
    print("---")
```

### **Reportes por cliente:**

```python
# Agrupar compras por cliente final
from collections import defaultdict

customer_purchases = defaultdict(list)

po_lines = env['purchase.order.line'].search([
    ('customer_id', '!=', False)
])

for po_line in po_lines:
    customer_purchases[po_line.customer_id.name].append({
        'po': po_line.order_id.name,
        'product': po_line.product_id.name,
        'amount': po_line.price_subtotal
    })

for customer, purchases in customer_purchases.items():
    total_amount = sum(p['amount'] for p in purchases)
    print(f"Cliente: {customer}")
    print(f"Total compras: €{total_amount:.2f}")
    print(f"Líneas: {len(purchases)}")
    for purchase in purchases[:3]:  # Mostrar primeras 3
        print(f"  - {purchase['po']}: {purchase['product']}")
    print("---")
```

## Ejemplo de Uso

### **Antes del módulo:**
```python
# Crear SO con producto MTO
so = sale_order.create({...})
so.action_confirm()  # Genera procurement → PO

po_line = purchase_order_line.search([('origin', 'like', so.name)])
print(po_line.sale_line_id)  # ❌ False (vacío)
print(po_line.customer_id)   # ❌ False (vacío)
```

### **Después del módulo:**
```python
# Mismo proceso
so = sale_order.create({...})
so.action_confirm()  # Genera procurement → PO

po_line = purchase_order_line.search([('origin', 'like', so.name)])
print(po_line.sale_line_id)  # ✅ sale.order.line(123,)
print(po_line.customer_id)   # ✅ res.partner(456,) - Cliente automático
```

## Testing

### **Test Básico:**

```python
def test_mto_linking():
    # 1. Crear producto MTO
    product = env['product.product'].create({
        'name': 'Test Product MTO',
        'type': 'product',
        'route_ids': [
            (6, 0, [
                env.ref('stock.route_warehouse0_mto').id,
                env.ref('purchase_stock.route_warehouse0_buy').id
            ])
        ],
        'seller_ids': [(0, 0, {
            'partner_id': env.ref('base.res_partner_1').id,
            'price': 100.0,
        })],
    })
    
    # 2. Crear SO
    so = env['sale.order'].create({
        'partner_id': env.ref('base.res_partner_12').id,
        'order_line': [(0, 0, {
            'product_id': product.id,
            'product_uom_qty': 5.0,
        })],
    })
    
    # 3. Confirmar
    so.action_confirm()
    env['procurement.group'].run_scheduler()
    
    # 4. Verificar
    po_line = env['purchase.order.line'].search([
        ('product_id', '=', product.id)
    ], limit=1)
    
    # Assertions
    assert po_line.sale_line_id, "sale_line_id should be set"
    assert po_line.customer_id, "customer_id should be calculated"
    assert po_line.customer_id == so.partner_id, "customer should match SO partner"
    
    print("✅ Test passed - MTO linking works!")

# test_mto_linking()
```

## Casos de Uso

### 📊 **Business Intelligence**
- Dashboards con trazabilidad SO → PO
- KPIs de márgenes por cliente
- Análisis de productos más rentables

### 🔄 **Automatizaciones**
- Scripts que actualizan precios basándose en márgenes
- Notificaciones cuando márgenes son bajos
- Sincronización con sistemas externos

### 📋 **Reportes Personalizados**
- Compras generadas por cliente específico
- Análisis de proveedores por cliente final
- Tracking de órdenes desde venta hasta compra

### 🎯 **Integraciones**
- APIs que necesitan vincular datos SO-PO
- Conectores con CRM/ERP externos
- Webhooks con información de trazabilidad

## Compatibilidad

- ✅ **Odoo 18.0**
- ✅ **Community & Enterprise**
- ✅ Compatible con dropshipping existente
- ✅ Compatible con servicios subcontratados
- ✅ Multi-company
- ✅ Multi-warehouse

## Soporte

Para uso programático, verificar:
1. Que el producto tenga rutas MTO + Buy
2. Que exista proveedor configurado
3. Que los procurements se ejecuten correctamente

```python
# Debug:
po_lines = env['purchase.order.line'].search([('sale_line_id', '!=', False)])
print(f"Líneas vinculadas encontradas: {len(po_lines)}")
```

## License

LGPL-3

---
**Versión:** Backend Only (sin vistas UI)  
**Funcionalidad:** ✅ Completa para uso programático  
**Vistas XML:** ❌ Eliminadas (solo backend)
