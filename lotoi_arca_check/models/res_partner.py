from datetime import timedelta

from odoo import _, fields, models

from . import arca_ws

STATUS = [
    ('active', 'CUIT activo'),
    ('inactive', 'CUIT inactivo'),
    ('not_found', 'CUIT inexistente'),
    ('constancia_error', 'Constancia con errores'),
    ('invalid', 'CUIT mal cargado'),
    ('error', 'No se pudo consultar'),
]
BLOCKING = ('inactive', 'not_found', 'constancia_error', 'invalid')


class ResPartner(models.Model):
    _inherit = 'res.partner'

    lotoi_arca_status = fields.Selection(STATUS, string='Estado en ARCA', readonly=True, copy=False)
    lotoi_arca_message = fields.Char(string='Detalle de ARCA', readonly=True, copy=False)
    lotoi_arca_checked_at = fields.Datetime(string='Consultado en ARCA', readonly=True, copy=False)

    def _lotoi_arca_applies(self):
        """Se controlan contactos argentinos con CUIT/CUIL (o con 11 digitos).

        Un CUIT cargado con otra cantidad de digitos tambien entra al control (queda como
        'invalid' y bloquea), para que un dato mal cargado no permita pagar sin aviso.
        """
        self.ensure_one()
        vat = arca_ws.digits(self.vat)
        if not vat or (self.country_id and self.country_id.code != 'AR'):
            return False
        code = self.l10n_latam_identification_type_id.l10n_ar_afip_code if 'l10n_latam_identification_type_id' in self._fields else False
        return len(vat) == 11 or code in ('80', '86')

    def _lotoi_arca_refresh(self, force=False):
        """Consulta ARCA si el ultimo resultado es viejo (o con force). Devuelve el estado."""
        self.ensure_one()
        hours = float(self.env['ir.config_parameter'].sudo().get_param('lotoi_arca_check.max_age_hours', '24'))
        fresh = (self.lotoi_arca_checked_at and self.lotoi_arca_status and self.lotoi_arca_status != 'error'
                 and self.lotoi_arca_checked_at > fields.Datetime.now() - timedelta(hours=hours))
        if force or not fresh:
            vat = arca_ws.digits(self.vat)
            if len(vat) != 11:
                res = {'status': 'invalid', 'name': '',
                       'message': _('El CUIT cargado tiene %s dígitos (deben ser 11). Corregirlo antes de pagar.', len(vat))}
            else:
                res = self.env['lotoi.arca.check'].check_cuit(self.vat)
            self.sudo().write({'lotoi_arca_status': res['status'], 'lotoi_arca_message': res['message'],
                               'lotoi_arca_checked_at': fields.Datetime.now()})
        return self.lotoi_arca_status

    def action_lotoi_arca_check(self):
        for partner in self:
            if not partner._lotoi_arca_applies():
                partner.sudo().write({'lotoi_arca_status': False,
                                      'lotoi_arca_message': _('Sin CUIT argentino para consultar.'),
                                      'lotoi_arca_checked_at': fields.Datetime.now()})
            else:
                partner._lotoi_arca_refresh(force=True)
        if len(self) == 1:
            status = dict(STATUS).get(self.lotoi_arca_status, '')
            return {'type': 'ir.actions.client', 'tag': 'display_notification', 'params': {
                'title': _('Consulta a ARCA'), 'message': '%s: %s' % (status, self.lotoi_arca_message or ''),
                'type': 'success' if self.lotoi_arca_status == 'active' else 'warning', 'sticky': False}}
