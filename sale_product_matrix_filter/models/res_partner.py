# Copyright 2023 Serincloud SL - Ingenieriacloud.com

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = "res.partner"


    # SALE ATTRIBUTE VALUES in customers:
    sale_filter_attribute_id = fields.Many2one('product.attribute', compute='_get_sale_filter_attribute_id')
    @api.depends('company_id.sale_filter_attribute_id')
    def _get_sale_filter_attribute_id(self):
        """Obtener el atributo de filtro de la company asociada"""
        for partner in self:
            partner.sale_filter_attribute_id = partner.env.company.sale_filter_attribute_id.id

    value_filter_ids = fields.Many2many(
        'product.attribute.value',
        'res_partner_attribute_value_rel',
        'partner_id',
        'attribute_value_id',
        string="Shipping mark",
        help="Selecciona valores de atributo para filtrar las variantes en la matriz."
    )
