# Partner Risk Insurance Extended

**Versión:** 18.0.1.0.1
**Autor:** AvanzOSC
**Licencia:** AGPL-3
**Categoría:** Credit Control

## Descripción

Módulo de extensión del control de riesgo financiero de partners. Complementa los módulos
`account_financial_risk`, `partner_risk_insurance`, `account_payment_return_financial_risk`
y `sale_financial_risk` con dos funcionalidades principales:

### 1. Valores por defecto a True

Al instalar el módulo, todos los campos de control de riesgo en `res.partner` se activan
por defecto tanto para registros existentes (vía `post_init_hook`) como para los nuevos:

| Campo | Descripción |
|---|---|
| `risk_sale_order_include` | Incluir pedidos de venta |
| `risk_invoice_draft_include` | Incluir facturas en borrador |
| `risk_invoice_open_include` | Incluir facturas abiertas / saldo principal |
| `risk_invoice_unpaid_include` | Incluir facturas impagadas / saldo principal |
| `risk_account_amount_include` | Incluir otras cuentas abiertas |
| `risk_account_amount_unpaid_include` | Incluir otras cuentas impagadas |
| `risk_payment_return_include` | Incluir devoluciones de pago |

### 2. Vista de seguimiento Partner Risks

Nueva vista accesible en **Contabilidad › Clientes › Partner Risks**, visible únicamente
para el grupo `account_financial_risk.group_account_financial_risk_user`.

#### Características de la vista

- **Lista con edición múltiple** (`multi_edit`) para modificar campos en bloque.
- **Dominio**: empresas (`is_company = True`) con monitorización activa
  (`risk_remaining_value_include = True`).
- **Campo `risk_remaining_value_include`**: booleano computado y almacenado que se activa
  automáticamente cuando al menos uno de los campos `_include` está habilitado.
- **Campo `risk_coverage_display`**: porcentaje de cobertura utilizada
  (`100 - risk_remaining_percentage`) formateado como `"X.XX%"`.

#### Columnas disponibles

| Campo | Visibilidad por defecto |
|---|---|
| Partner (name) | Siempre visible |
| Credit Limit | Siempre visible |
| Company Credit Limit | Opcional (visible) |
| Insured Credit Limit | Opcional (visible) |
| Risk Remaining Value | Opcional (visible) |
| Cobertura (risk_coverage_display) | Opcional (visible) |
| Risk Remaining % | Opcional (oculto) |
| Total Risk | Opcional (visible) |
| Insurance Code | Opcional (oculto) |
| Insurance Requested | Opcional (oculto) |
| Insurance Grant Date | Opcional (oculto) |
| Credit Policy State | Opcional (visible) |
| Credit Policy Company | Opcional (oculto) |
| Insurance Coverage % | Opcional (oculto) |
| Risk Amount Exceeded | Opcional (oculto) |
| Risk Exception | Opcional (oculto) |
| Risk Sale Order | Opcional (oculto) |
| Invoice Draft Risk | Opcional (oculto) |
| Risk Invoice Open | Opcional (oculto) |
| Risk Invoice Unpaid | Opcional (oculto) |
| Risk Account Amount | Opcional (oculto) |
| Risk Account Amount Unpaid | Opcional (oculto) |
| Risk Payment Return | Opcional (oculto) |

#### Colores en la vista lista

- **`risk_remaining_value` y `risk_coverage_display`**: verde si hay margen positivo,
  rojo si el riesgo supera el límite de crédito.
- **Campos de riesgo individuales** (`risk_sale_order`, `risk_invoice_draft`, etc.):
  - 🔴 Rojo: `_include = True` y valor supera su límite específico (`*_limit`)
  - 🟢 Verde: `_include = True` y valor > 0 pero dentro del límite
  - Sin color: `_include = False` o valor = 0

#### Filtros de búsqueda

- Include in Risk Monitoring
- Sales Orders Risk (include + valor > 0)
- Draft Invoice Risk (include + valor > 0)
- Open Invoice Risk (include + valor > 0)
- Unpaid Invoice Risk (include + valor > 0)
- Account Amount Risk (include)
- Account Unpaid Risk (include)
- Payment Return Risk (include + valor > 0)
- Risk Exception
- Amount Exceeded

#### Agrupar por

- Credit Policy Company
- Credit Policy State

## Dependencias

- `account_financial_risk`
- `partner_risk_insurance`
- `account_payment_return_financial_risk`
- `sale_financial_risk`
