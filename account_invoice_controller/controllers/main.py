import json
import logging
from odoo import http
from odoo.http import request
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class InvoiceWebhookController(http.Controller):
    @http.route('/api/a7k9m3x2w8v5n1q6z4r0', type='json', auth='public', methods=['POST'], csrf=False)
    def create_invoice_from_json(self, **kwargs):
        """
        Endpoint SEGURO para crear una factura y su partner desde un JSON.
        Requiere token de autenticación válido en header X-API-TOKEN.
        """
        
        # --- VALIDACIÓN DE SEGURIDAD CON TOKEN DE BASE DE DATOS ---
        api_token = request.httprequest.headers.get('X-API-TOKEN')
        client_ip = request.httprequest.environ.get('REMOTE_ADDR', 'unknown')

        # Buscar y validar token en la base de datos
        token_record, message = request.env['webhook.token'].sudo().find_valid_token(api_token, client_ip)
        
        if not token_record:
            _logger.warning(f"Acceso webhook no autorizado desde IP: {client_ip}, Token: {api_token}, Error: {message}")
            return {
                'status': 'error', 
                'message': f'Acceso no autorizado: {message}',
                'code': 'UNAUTHORIZED'
            }
        
        # Log de acceso autorizado
        _logger.info(f"Acceso webhook autorizado desde IP: {client_ip}, Usuario: {token_record.user_id.name}")
        
        # Marcar token como usado
        token_record.mark_as_used(client_ip)
        
        # Cambiar el contexto de ejecución al usuario del token
        request.env = request.env(user=token_record.user_id.id)
        # El payload JSON se obtiene con el método get_json_data()
        payload = request.get_json_data() # <-- LÍNEA CORREGIDA

        try:
            # --- 1. Validaciones iniciales ---
            partner_data = payload.get('partner')
            if not partner_data or not partner_data.get('vat'):
                return {'status': 'error', 'message': "El JSON debe incluir un objeto 'partner' con un campo 'vat'."}

            # --- 2. Validar datos de factura ANTES de crear el partner ---
            invoice_data = payload.get('invoice')
            if not invoice_data or not invoice_data.get('lines'):
                return {'status': 'error', 'message': "El JSON debe incluir un objeto 'invoice' con una lista 'lines'."}

            # Validar que las líneas de productos existen ANTES de crear el partner
            for line in invoice_data['lines']:
                display_type = line.get('display_type', False)
                # Solo validar productos (no secciones ni notas)
                if not display_type or display_type not in ['line_section', 'line_note']:
                    if not line.get('product_ref'):
                        return {'status': 'error', 'message': "Las líneas de producto deben incluir 'product_ref'."}
                    product = request.env['product.product'].sudo().search([('default_code', '=', line.get('product_ref'))], limit=1)
                    if not product:
                        return {'status': 'error', 'message': f"Producto con referencia '{line.get('product_ref')}' no encontrado."}

            # --- 3. Búsqueda o creación del cliente (Partner) ---
            # Solo llegamos aquí si la factura es válida
            vat = partner_data['vat']
            partner = request.env['res.partner'].sudo().search([('vat', '=', vat)], limit=1)

            if not partner:
                # Búsqueda de país por código o nombre
                country_id = False
                if partner_data.get('country') or partner_data.get('country_code'):
                    country_search = partner_data.get('country_code') or partner_data.get('country')
                    country = request.env['res.country'].sudo().search([
                        '|', ('code', '=ilike', country_search), ('name', '=ilike', country_search)
                    ], limit=1)
                    if country:
                        country_id = country.id
                
                # Búsqueda de estado/provincia por código o nombre
                state_id = False
                if partner_data.get('state') or partner_data.get('state_code'):
                    state_search = partner_data.get('state_code') or partner_data.get('state')
                    state = request.env['res.country.state'].sudo().search([
                        '|', ('code', '=ilike', state_search), ('name', '=ilike', state_search)
                    ], limit=1)
                    if state:
                        state_id = state.id

                # Campos estándar del partner
                partner_values = {
                    'name': partner_data.get('name'),
                    'vat': vat,
                    'email': partner_data.get('email'),
                    'phone': partner_data.get('phone'),
                    'mobile': partner_data.get('mobile'),
                    'website': partner_data.get('website'),
                    'street': partner_data.get('street'),
                    'street2': partner_data.get('street2'),
                    'city': partner_data.get('city'),
                    'zip': partner_data.get('zip'),
                    'country_id': country_id,
                    'state_id': state_id,
                }
                
                # Campos de custom_innovalis (PNT - no MIG)
                innovalis_fields = {
                    'pnt_active_amount': partner_data.get('pnt_active_amount'),
                    'pnt_employee_qty': partner_data.get('pnt_employee_qty'),
                    'pnt_ebit': partner_data.get('pnt_ebit'),
                    'pnt_group_company_qty': partner_data.get('pnt_group_company_qty'),
                    'pnt_limit_contract_date': partner_data.get('pnt_limit_contract_date'),
                    'pnt_end_date': partner_data.get('pnt_end_date'),
                    'pnt_end_subject': partner_data.get('pnt_end_subject'),
                    'pnt_km': partner_data.get('pnt_km'),
                    'pnt_sale_amount': partner_data.get('pnt_sale_amount'),
                    'pnt_anhodisponible': partner_data.get('pnt_anhodisponible'),
                    'pnt_resultadoantesimpuesto': partner_data.get('pnt_resultadoantesimpuesto'),
                    'pnt_impuestosociedades': partner_data.get('pnt_impuestosociedades'),
                    'pnt_director': partner_data.get('pnt_director'),
                    'pnt_auditor': partner_data.get('pnt_auditor'),
                    'pnt_catastro': partner_data.get('pnt_catastro'),
                }
                
                # Combinar todos los campos y filtrar valores None/vacíos
                partner_values.update(innovalis_fields)
                partner_values = {k: v for k, v in partner_values.items() if v is not None and v != ''}
                partner = request.env['res.partner'].sudo().create(partner_values)

            # --- 4. Creación de la Factura (Invoice) ---
            # Los datos ya están validados anteriormente
            invoice_lines = []
            for line in invoice_data['lines']:
                display_type = line.get('display_type', False)
                
                if display_type == 'line_section':
                    # Línea de sección
                    invoice_lines.append((0, 0, {
                        'display_type': 'line_section',
                        'name': line.get('name', 'Sección'),
                    }))
                elif display_type == 'line_note':
                    # Línea de nota
                    invoice_lines.append((0, 0, {
                        'display_type': 'line_note', 
                        'name': line.get('name', 'Nota'),
                    }))
                else:
                    # Línea de producto (ya validado que existe)
                    product = request.env['product.product'].sudo().search([('default_code', '=', line.get('product_ref'))], limit=1)
                    invoice_lines.append((0, 0, {
                        'product_id': product.id,
                        'name': line.get('description', product.name),
                        'quantity': line.get('quantity', 1),
                        'price_unit': line.get('price_unit'),
                    }))

            invoice_values = {
                'partner_id': partner.id,
                'move_type': 'out_invoice',
                'invoice_date': invoice_data.get('date'),
                'invoice_line_ids': invoice_lines,
            }
            new_invoice = request.env['account.move'].sudo().create(invoice_values)

            # Log de éxito
            _logger.info(f"Factura creada: {new_invoice.name} para partner: {partner.name} por usuario: {token_record.user_id.name}")

            # Devolvemos una respuesta de éxito
            return {
                'status': 'success',
                'invoice_id': new_invoice.id,
                'invoice_name': new_invoice.name,
                'partner_id': partner.id,
                'partner_name': partner.name,
                'created_by': token_record.user_id.name,
                'token_name': token_record.name
            }

        except Exception as e:
            # Log del error con información del usuario
            _logger.error(f"Error en webhook para usuario {token_record.user_id.name}: {str(e)}", exc_info=True)
            # Capturamos cualquier error para devolver una respuesta clara
            return {'status': 'error', 'message': str(e)}
