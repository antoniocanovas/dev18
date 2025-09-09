# Ejemplos Prácticos - Purchase Lot Preassignment

## Caso de Uso Completo: Empresa de Electrónicos

### Escenario
Una empresa compra componentes electrónicos que requieren números de serie únicos.

### Paso a Paso

#### 1. Configuración Producto
```
Producto: "Microcontrolador ESP32"
Código: ESP32-WROOM
Tracking: By Unique Serial Number
```

#### 2. Crear Pedido de Compra
```
Proveedor: ElectroComponents Inc.
Producto: ESP32-WROOM
Cantidad: 10 unidades
```

#### 3. Generar Lotes Pre-asignados
- Hacer clic en **"Generate Lots"**
- El sistema crea automáticamente:
  ```
  ESP32-PO0001-SN0001
  ESP32-PO0001-SN0002
  ESP32-PO0001-SN0003
  ...
  ESP32-PO0001-SN0010
  ```

#### 4. Compartir con Proveedor
Enviar lista de números de serie esperados:
```
Pedido: PO0001
Producto: ESP32-WROOM
Números de Serie Esperados:
- ESP32-PO0001-SN0001
- ESP32-PO0001-SN0002
- ESP32-PO0001-SN0003
- ...
```

#### 5. Recepción y Validación
Al recibir el producto:
- **Verde**: Números coinciden ✅
- **Naranja**: Números diferentes ⚠️
- **Mensaje**: "Received ESP32-PO0001-SN0005 but expected ESP32-PO0001-SN0004"

## Caso 2: Industria Farmacéutica

### Escenario
Compra de medicamentos que se manejan por lotes.

#### Configuración
```
Producto: "Antibiótico 500mg"
Código: ANT500
Tracking: By Lots
Lote Size: 1000 unidades
```

#### Pedido
```
Cantidad: 5000 unidades
Lotes generados:
- ANT500-PO0123-L001 (1000 uds)
- ANT500-PO0123-L002 (1000 uds)
- ANT500-PO0123-L003 (1000 uds)
- ANT500-PO0123-L004 (1000 uds)
- ANT500-PO0123-L005 (1000 uds)
```

## Caso 3: Manufactura Automotriz

### Escenario
Piezas críticas con números de serie para trazabilidad.

#### Workflow Completo

**1. Configuración Inicial**
```python
# Producto en Odoo
{
    'name': 'Sensor ABS Delantero',
    'default_code': 'SENS-ABS-001',
    'tracking': 'serial',
    'categ_id': 'Sensores Automotrices'
}
```

**2. Pedido de Compra**
- 20 sensores ABS
- Proveedor: AutoParts GmbH
- Fecha entrega: 15 días

**3. Generación Automática**
```
Lotes Pre-asignados:
SENS-ABS-001-PO0456-SN0001
SENS-ABS-001-PO0456-SN0002
...
SENS-ABS-001-PO0456-SN0020
```

**4. Comunicación con Proveedor**
Email automático con lista de números esperados para etiquetado.

**5. Control de Calidad en Recepción**
- Validación automática de números de serie
- Registro de discrepancias
- Trazabilidad completa desde compra hasta cliente final

## Personalización Avanzada

### Nomenclatura Personalizada por Empresa

#### Modificar generación de lotes:
```python
def _generate_lot_name(self, line, sequence):
    """Nomenclatura personalizada"""
    company_code = self.company_id.code or 'COM'
    date_str = fields.Date.today().strftime('%Y%m')
    product_code = line.product_id.default_code or 'PROD'
    
    if line.product_id.tracking == 'serial':
        return f"{company_code}-{product_code}-{date_str}-{sequence:05d}"
    else:
        return f"LOT-{company_code}-{product_code}-{date_str}-{sequence:03d}"
```

#### Resultado:
```
Series: ABC-SENS001-202501-00001
Lotes:  LOT-ABC-SENS001-202501-001
```

### Integración con Sistema Externo

#### Webhook para notificar al proveedor:
```python
def action_confirm(self):
    """Notificar proveedor automáticamente"""
    res = super().action_confirm()
    
    # Enviar lotes esperados por API
    if self.lot_preassignment_ids:
        self._send_expected_lots_to_vendor()
    
    return res

def _send_expected_lots_to_vendor(self):
    """Envío por webhook/API"""
    data = {
        'purchase_order': self.name,
        'vendor_id': self.partner_id.id,
        'expected_lots': [
            {
                'product_code': lot.product_id.default_code,
                'lot_name': lot.name,
                'quantity': lot.product_qty
            }
            for lot in self.lot_preassignment_ids
        ]
    }
    # Enviar a sistema externo
```

## Reportes y Analytics

### Informe de Conformidad de Lotes
```sql
SELECT 
    po.name as purchase_order,
    pp.default_code as product_code,
    COUNT(pla.id) as expected_lots,
    COUNT(CASE WHEN pla.state = 'received' THEN 1 END) as received_lots,
    COUNT(CASE WHEN pla.state = 'received' THEN 1 END) * 100.0 / COUNT(pla.id) as conformity_rate
FROM purchase_lot_preassignment pla
JOIN purchase_order po ON pla.purchase_order_id = po.id
JOIN product_product pp ON pla.product_id = pp.id
GROUP BY po.name, pp.default_code
ORDER BY conformity_rate DESC;
```

### Dashboard de Trazabilidad
- % de lotes recibidos correctamente
- Tiempo promedio entre confirmación y recepción
- Proveedores con mayor conformidad
- Productos con más discrepancias

## Flujo de Integración Completa

### 1. ERP → Proveedor
```json
{
    "purchase_order": "PO0001",
    "expected_delivery": "2025-01-15",
    "products": [
        {
            "code": "PROD001",
            "quantity": 100,
            "expected_lots": ["LOT-001", "LOT-002"]
        }
    ]
}
```

### 2. Proveedor → ERP (Confirmación)
```json
{
    "purchase_order": "PO0001",
    "status": "confirmed",
    "assigned_lots": ["LOT-001", "LOT-002"],
    "shipment_date": "2025-01-14"
}
```

### 3. Recepción → Validación
```json
{
    "purchase_order": "PO0001",
    "received_lots": ["LOT-001", "LOT-003"],
    "discrepancies": [
        {"expected": "LOT-002", "received": "LOT-003"}
    ]
}
```

Este módulo proporciona la base completa para implementar trazabilidad proactiva en compras, mejorando la comunicación con proveedores y el control de calidad en recepción.
