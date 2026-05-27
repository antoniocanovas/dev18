# Copyright 2024 Ingenieriacloud.com

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    shoes_samples = fields.Boolean(
        'Shoes Samples',
        help='Marca esta casilla si este contacto es un agente y le vas a enviar muestras',
    )

    shoes_sample_ids = fields.One2many(
        'shoes.sample', 'partner_id', string='Samples'
    )
    shoes_sample_count = fields.Integer('Samples', compute='_compute_shoes_sample_count')

    @api.depends('shoes_sample_ids')
    def _compute_shoes_sample_count(self):
        for partner in self:
            partner.shoes_sample_count = len(partner.shoes_sample_ids)

    def action_view_ship_demo(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Samples',
            'res_model': 'shoes.sample',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
