# -*- coding: utf-8 -*-

import secrets
import string
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class WebhookToken(models.Model):
    _name = 'webhook.token'
    _description = 'Token de acceso para Webhook'
    _rec_name = 'name'
    _order = 'create_date desc'

    name = fields.Char(
        string='Nombre del Token',
        required=True,
        help="Nombre descriptivo para identificar el token"
    )

    token = fields.Char(
        string='Token de API',
        required=True,
        readonly=True,
        copy=False,
        default=lambda self: self._generate_token(),
        help="Token de autenticación para el webhook"
    )

    user_id = fields.Many2one(
        'res.users',
        string='Usuario',
        required=True,
        default=lambda self: self.env.user,
        help="Usuario propietario del token. Las operaciones se ejecutarán con sus permisos."
    )

    active = fields.Boolean(
        string='Activo',
        default=True,
        help="Si está inactivo, el token no funcionará"
    )

    last_used = fields.Datetime(
        string='Último uso',
        readonly=True,
        help="Fecha y hora del último uso del token"
    )

    usage_count = fields.Integer(
        string='Veces usado',
        readonly=True,
        default=0,
        help="Número de veces que se ha usado el token"
    )

    description = fields.Text(
        string='Descripción',
        help="Descripción detallada del propósito de este token"
    )

    expiry_date = fields.Datetime(
        string='Fecha de caducidad',
        help="El token dejará de funcionar después de esta fecha"
    )

    allowed_ips = fields.Text(
        string='IPs Permitidas',
        help="Lista de IPs permitidas (una por línea). Dejar vacío para permitir todas."
    )

    # El método create adaptado para Odoo 18 sigue siendo una buena práctica
    # para la creación de registros desde código.
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('token'):
                vals['token'] = self._generate_token()
        return super().create(vals_list)

    # El método _generate_token ahora se usa tanto en el default como en el create.
    # No necesita ser un método de la clase, puede ser estático.
    @api.model
    def _generate_token(self):
        """Genera un token seguro de 32 caracteres"""
        alphabet = string.ascii_letters + string.digits
        return 'whk_' + ''.join(secrets.choice(alphabet) for i in range(32))

    def regenerate_token(self):
        """Regenera el token manualmente"""
        for record in self:
            record.token = self._generate_token()

    def mark_as_used(self, client_ip=None):
        """Marca el token como usado y actualiza estadísticas"""
        self.ensure_one()
        self.sudo().write({
            'last_used': fields.Datetime.now(),
            'usage_count': self.usage_count + 1
        })

    @api.constrains('expiry_date')
    def _check_expiry_date(self):
        for record in self:
            if record.expiry_date and record.expiry_date <= fields.Datetime.now():
                raise ValidationError("La fecha de caducidad debe ser futura")

    def is_valid(self, client_ip=None):
        """Verifica si el token es válido"""
        self.ensure_one()

        if not self.active:
            return False, "Token inactivo"

        if self.expiry_date and self.expiry_date <= fields.Datetime.now():
            return False, "Token caducado"

        if self.allowed_ips and client_ip:
            allowed_list = [ip.strip() for ip in self.allowed_ips.split('\n') if ip.strip()]
            if allowed_list and client_ip not in allowed_list:
                return False, f"IP {client_ip} no autorizada"

        if not self.user_id.active:
            return False, "Usuario asociado inactivo"

        return True, "Token válido"

    @api.model
    def find_valid_token(self, token_value, client_ip=None):
        """Busca y valida un token"""
        if not token_value:
            return None, "Token requerido"

        token_record = self.search([('token', '=', token_value)], limit=1)
        if not token_record:
            return None, "Token no encontrado"

        is_valid, message = token_record.is_valid(client_ip)
        if not is_valid:
            return None, message

        return token_record, "Token válido"