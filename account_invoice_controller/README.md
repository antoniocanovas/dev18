# Account Invoice Controller

Módulo de Odoo para crear facturas de cliente através de webhook JSON con autenticación por tokens.

## Descripción

Este módulo permite crear facturas de cliente desde sistemas externos mediante una API REST que acepta datos JSON. Incluye creación automática de partners si no existen y soporte para líneas de factura con secciones y notas.

## Características

- **Webhook seguro** con autenticación por tokens de usuario
- **Creación automática de partners** con datos completos
- **Soporte para campos personalizados** de custom_innovalis
- **Líneas de factura estructuradas** (productos, secciones, notas)
- **Gestión completa de tokens** desde la interfaz de Odoo
- **Auditoría y logging** de todos los accesos
- **Control de seguridad** por IP y fechas de caducidad

## Instalación

1. Copiar el módulo a la carpeta de addons de Odoo
2. Actualizar la lista de módulos en Apps
3. Instalar "Account Invoice Controller"

## Configuración

### Crear un token de acceso:

1. Ir a **Webhook Facturas > Tokens de API**
2. Crear nuevo token con:
   - Nombre descriptivo
   - Usuario asociado
   - Fecha de caducidad (opcional)
   - IPs permitidas (opcional)
3. Copiar el token generado

### Usar el webhook:

**URL:** `http://tu-odoo.com/api/a7k9m3x2w8v5n1q6z4r0`  
**Método:** POST  
**Headers:**
- `Content-Type: application/json`
- `X-API-TOKEN: tu_token_aqui`

## Ejemplo de uso

```bash
curl -X POST http://localhost:8069/api/a7k9m3x2w8v5n1q6z4r0 \
  -H "Content-Type: application/json" \
  -H "X-API-TOKEN: whk_abc123..." \
  -d '{
    "partner": {
      "name": "Cliente Ejemplo",
      "vat": "ESA12345674",
      "email": "cliente@ejemplo.com"
    },
    "invoice": {
      "date": "2025-01-15",
      "lines": [
        {
          "product_ref": "PROD001",
          "quantity": 1,
          "price_unit": 100.00
        }
      ]
    }
  }'
```

## Estructura JSON

### Partner (obligatorio)
- `name`: Nombre de la empresa (obligatorio)
- `vat`: NIF/CIF (obligatorio)
- `email`, `phone`, `mobile`: Datos de contacto
- `street`, `street2`, `city`, `zip`: Dirección
- `country`, `state`: País y provincia (por nombre o código)
- `website`: Sitio web
- Campos custom_innovalis (pnt_*)

### Invoice (obligatorio)
- `date`: Fecha de la factura
- `lines`: Array de líneas (obligatorio)

### Líneas de factura
- **Producto**: `product_ref`, `description`, `quantity`, `price_unit`
- **Sección**: `display_type: "line_section"`, `name`
- **Nota**: `display_type: "line_note"`, `name`

## Respuestas

### Éxito
```json
{
  "status": "success",
  "invoice_id": 123,
  "invoice_name": "INV/2025/0001",
  "partner_id": 456,
  "partner_name": "Cliente Ejemplo",
  "created_by": "Administrator",
  "token_name": "Mi Token"
}
```

### Error
```json
{
  "status": "error",
  "message": "Descripción del error",
  "code": "UNAUTHORIZED"
}
```

## Seguridad

- Tokens únicos por usuario con permisos heredados
- Control de acceso por IP opcional
- Fechas de caducidad configurables
- Logging completo de accesos
- Desactivación instantánea de tokens

## Dependencias

- `base`: Módulo base de Odoo
- `account`: Contabilidad
- `product`: Productos
- `custom_innovalis`: Módulo personalizado con campos PNT

## Soporte

Para issues y mejoras, contactar con el equipo de desarrollo.

## Licencia

LGPL-3
