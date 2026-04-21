Extiende los módulos de riesgo financiero de partner estableciendo los campos
de control de riesgo a **True** por defecto para todos los partners y creando
una nueva vista de seguimiento en **Contabilidad › Clientes › Partner Risks**.

## Valores por defecto

Los siguientes campos de `res.partner` se establecen a `True` por defecto
para nuevos registros y en la instalación del módulo para registros existentes:

- `risk_sale_order_include` — Incluir Pedidos de Venta
- `risk_invoice_draft_include` — Incluir Facturas en Borrador
- `risk_invoice_open_include` — Incluir Facturas Abiertas / Saldo Principal
- `risk_invoice_unpaid_include` — Incluir Facturas Impagadas / Saldo Principal
- `risk_account_amount_include` — Incluir Otras Cuentas Abiertas
- `risk_account_amount_unpaid_include` — Incluir Otras Cuentas Impagadas
- `risk_payment_return_include` — Incluir Devoluciones de Pago

## Nueva vista Partner Risks

Vista de lista con edición múltiple, dominio sobre empresas con
`risk_remaining_value > 0`, filtros por cada tipo de riesgo y agrupación
por compañía aseguradora y estado de póliza. Visible solo para el grupo
`account_financial_risk.group_account_financial_risk_user`.
