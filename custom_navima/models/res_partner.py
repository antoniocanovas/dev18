# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Campos de migración facilitados por el cliente, se pueden eliminar en un futuro
    # para PROVEEDORES (de momento):
    mig_subcuenta = fields.Char("mig_subcuenta")
    mig_agente = fields.Char("mig_agente")
    mig_inconterm = fields.Char("mig_inconterm")
    mig_fpago = fields.Char("mig_fpago")
    mig_aseguradora = fields.Char("mig_aseguradora")
    mig_concedido = fields.Char("mig_concedido")
    mig_posicionfiscal = fields.Char("mig_posicionfiscal")
    mig_responsableinterno = fields.Char("mig_responsableinterno")
    mig_provincia = fields.Char("mig_provincia")
    mig_vat = fields.Char("mig_vat")
    mig_nombrecomercial = fields.Char("mig_nombrecomercial")

    # Campo para etiquetas imprimibles reutilizando res.partner.category
    printed_label_ids = fields.Many2many(
        "res.partner.category",
        "res_partner_printed_label_rel",
        "partner_id",
        "category_id",
        string="Etiquetas Imprimibles",
        help="Etiquetas que se mostrarán en formatos impresos como presupuestos y"
        " facturas. "
        'Por ejemplo: "NO PIG", "ECOLOGIC", etc.',
    )
