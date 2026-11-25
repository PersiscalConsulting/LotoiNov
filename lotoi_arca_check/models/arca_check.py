import base64
import logging

import requests

from odoo import api, fields, models
from odoo.exceptions import UserError

from . import arca_ws

_logger = logging.getLogger(__name__)
TIMEOUT = 25


class LotoiArcaToken(models.Model):
    """Ticket de acceso (token y firma) de WSAA, guardado para reutilizarlo.

    WSAA no entrega un ticket nuevo mientras el anterior siga vigente, por eso se guarda.
    """
    _name = 'lotoi.arca.token'
    _description = 'Ticket de acceso a ARCA (constancia de inscripcion)'
    _order = 'id desc'

    company_id = fields.Many2one('res.company', required=True, ondelete='cascade')
    environment = fields.Char(required=True)
    token = fields.Text()
    sign = fields.Text()
    expiration = fields.Datetime()


class LotoiArcaCheck(models.AbstractModel):
    _name = 'lotoi.arca.check'
    _description = 'Consulta de la constancia de inscripcion de un CUIT en ARCA'

    @api.model
    def _post(self, url, body):
        try:
            resp = requests.post(url, data=body, timeout=TIMEOUT,
                                 headers={'Content-Type': 'text/xml; charset=utf-8', 'SOAPAction': ''})
        except requests.RequestException as e:
            raise arca_ws.ArcaError('No se pudo conectar con ARCA: %s' % e)
        # ARCA responde 500 con un "fault" cuando hay un error de negocio: el contenido se interpreta igual
        if resp.status_code not in (200, 500):
            raise arca_ws.ArcaError('ARCA respondio HTTP %s' % resp.status_code)
        return resp.content

    @api.model
    def _credentials(self, company):
        crt, key = company.l10n_ar_afip_ws_crt_id, company.l10n_ar_afip_ws_key_id
        if not crt or not key:
            raise arca_ws.ArcaError('La compania no tiene cargados el certificado y la clave de ARCA.')
        cert_pem = base64.b64decode(crt.sudo().pem_certificate or b'')
        key_pem = base64.b64decode(key.sudo().pem_key or b'')
        if not cert_pem or not key_pem:
            raise arca_ws.ArcaError('No se pudo leer el certificado o la clave de ARCA.')
        return cert_pem, key_pem

    @api.model
    def _access_ticket(self, company):
        env = company.l10n_ar_afip_ws_environment or 'testing'
        Token = self.env['lotoi.arca.token'].sudo()
        now = fields.Datetime.now()
        cached = Token.search([('company_id', '=', company.id), ('environment', '=', env),
                               ('expiration', '>', fields.Datetime.add(now, minutes=5))], limit=1)
        if cached:
            return cached.token, cached.sign, env
        cert_pem, key_pem = self._credentials(company)
        cms = arca_ws.sign_tra(arca_ws.build_tra(), cert_pem, key_pem)
        content = self._post(arca_ws.URLS[env]['wsaa'], arca_ws.build_login_envelope(cms))
        token, sign, expiration = arca_ws.parse_login_response(content)
        Token.search([('company_id', '=', company.id), ('environment', '=', env)]).unlink()
        Token.create({'company_id': company.id, 'environment': env, 'token': token, 'sign': sign,
                      'expiration': expiration})
        return token, sign, env

    @api.model
    def check_cuit(self, cuit, company=None):
        """Consulta ARCA. Devuelve {'status', 'message', 'name'}.

        status: active | inactive | not_found | constancia_error | error
        (error = no se pudo consultar: no es un problema del CUIT).
        """
        company = company or self.env.company
        cuit = arca_ws.digits(cuit)
        try:
            token, sign, env = self._access_ticket(company)
            cuit_rep = arca_ws.digits(company.vat)
            content = self._post(arca_ws.URLS[env]['padron'],
                                 arca_ws.build_persona_envelope(token, sign, cuit_rep, cuit))
            return arca_ws.parse_persona_response(content)
        except arca_ws.ArcaError as e:
            _logger.warning('Consulta a ARCA del CUIT %s fallida: %s', cuit, e)
            return {'status': 'error', 'message': str(e), 'name': ''}
