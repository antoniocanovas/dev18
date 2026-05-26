# Copyright 2024 Ingenieriacloud.com

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shoes_samples = fields.Boolean(
        'Shoes Samples',
        help='Marca esta casilla si este contacto es un agente y le vas a enviar muestras',
    )

    shoes_referrer_ids = fields.One2many(
        'shoes.stock.referrer', 'partner_id', string='Ship demo'
    )
    shoes_referrer_count = fields.Integer('Ship demo', compute='_compute_shoes_referrer_count')

    @api.depends('shoes_referrer_ids')
    def _compute_shoes_referrer_count(self):
        for partner in self:
            partner.shoes_referrer_count = len(partner.shoes_referrer_ids)

    def action_view_ship_demo(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ship demo',
            'res_model': 'shoes.stock.referrer',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
