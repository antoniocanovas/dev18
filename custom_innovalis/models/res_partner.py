# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Campo de moneda para los campos monetarios
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id,
        help="Moneda para los campos monetarios"
    )
    
    # Campos PNT (Personal/Financial)
    pnt_active_amount = fields.Monetary(
        string="Total Activo",
        currency_field='currency_id',
        help="Total de activos del cliente"
    )

    pnt_employee_qty = fields.Integer(
        string="Nº empleados",
        help="Total de empleados del cliente"
    )

    pnt_ebit = fields.Monetary(
        string="Resultado Ejercicio",
        currency_field='currency_id',
        help="Resultado del ejercicio (EBIT)"
    )
    
    pnt_group_company_qty = fields.Integer(
        string="Nº Empresas",
        help="Número de empresas en el grupo"
    )
    
    pnt_limit_contract_date = fields.Date(
        string="Caducidad Contrato",
        help="Fecha de caducidad del contrato"
    )
    
    pnt_end_date = fields.Date(
        string="Fecha De Baja",
        help="Fecha en que se dio de baja al cliente"
    )
    
    pnt_end_subject = fields.Char(
        string="Motivo De La Baja",
        help="Motivo por el cual se dio de baja al cliente"
    )
    
    pnt_km = fields.Float(
        string="Distancia",
        digits=(8, 2),
        help="Distancia en kilómetros"
    )
    
    pnt_sale_amount = fields.Monetary(
        string="Volumen Negocio",
        currency_field='currency_id',
        help="Volumen de negocio con el cliente"
    )
    
    pnt_anhodisponible = fields.Date(
        string="Año actualización",
        help="Fecha del último año disponible"
    )
    
    pnt_resultadoantesimpuesto = fields.Monetary(
        string="Antes de Impuestos",
        currency_field='currency_id',
        help="Resultados antes de impuestos"
    )
    
    pnt_impuestosociedades = fields.Monetary(
        string="Imp. Sociedades",
        currency_field='currency_id',
        help="Impuesto de sociedades"
    )
    
    pnt_director = fields.Char(
        string="Director Ejecutivo",
        help="Nombre del director ejecutivo"
    )
    
    pnt_auditor = fields.Char(
        string="Auditora",
        help="Empresa auditora"
    )
    
    pnt_catastro = fields.Char(
        string="Referencia Catastral",
        help="Referencia catastral de la propiedad"
    )

    # Campos MIG (Migration/Management)
    mig_cuentacontable = fields.Char(
        string="Cuenta de Cliente",
        help="Cuenta contable asociada al cliente"
    )
    
    mig_cnae = fields.Char(
        string="CNAE",
        help="Código Nacional de Actividades Económicas"
    )
    
    mig_responsable = fields.Char(
        string="Responsable",
        help="Persona responsable del cliente"
    )
    
    mig_estado = fields.Char(
        string="Estado",
        help="Estado actual del cliente"
    )
    
    mig_formadepago = fields.Char(
        string="Forma De Pago",
        help="Forma de pago preferida del cliente"
    )
    
    mig_retencion = fields.Char(
        string="% Retención",
        help="Porcentaje de retención aplicable"
    )
    
    mig_prefijocuentacontable = fields.Char(
        string="Prefijo Cuenta",
        help="Prefijo para la cuenta contable"
    )
    
    mig_cuentacontableproveedor = fields.Char(
        string="Cuenta Proveedor",
        help="Cuenta contable cuando actúa como proveedor"
    )
