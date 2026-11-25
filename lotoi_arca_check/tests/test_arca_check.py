from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.addons.account.tests.common import AccountTestInvoicingCommon

CHECK = 'odoo.addons.lotoi_arca_check.models.arca_check.LotoiArcaCheck.check_cuit'


def _answer(status, message=''):
    return lambda self, cuit, company=None: {'status': status, 'message': message or status, 'name': ''}


@tagged('post_install', '-at_install')
class TestArcaCheck(AccountTestInvoicingCommon):
    """Ninguna prueba llama a ARCA: se reemplaza la consulta (check_cuit)."""

    def _payment(self, partner):
        return self.env['account.payment'].create({
            'payment_type': 'outbound', 'partner_type': 'supplier', 'partner_id': partner.id,
            'amount': 1.0, 'journal_id': self.company_data['default_journal_bank'].id,
        })

    def _partner(self, vat, **kw):
        return self.env['res.partner'].create({'name': 'Proveedor prueba ARCA', 'vat': vat, **kw})

    def test_blocks_inactive_cuit_even_without_bills(self):
        partner = self._partner('20000000117')       # sin facturas: supplier_rank = 0
        pay = self._payment(partner)
        with patch(CHECK, _answer('inactive')), self.assertRaises(UserError):
            pay.action_post()
        self.assertEqual(pay.state, 'draft')

    def test_blocks_not_found_and_constancia_error(self):
        for status in ('not_found', 'constancia_error'):
            pay = self._payment(self._partner('20000000117'))
            with patch(CHECK, _answer(status)), self.assertRaises(UserError):
                pay.action_post()

    def test_blocks_malformed_cuit_without_calling_arca(self):
        partner = self._partner('20-00000001-17', l10n_latam_identification_type_id=self.env.ref('l10n_ar.it_cuit').id)  # 12 digitos
        pay = self._payment(partner)
        with patch(CHECK, side_effect=AssertionError('no debe consultar ARCA')), self.assertRaises(UserError):
            pay.action_post()

    def test_allows_active_cuit(self):
        pay = self._payment(self._partner('30715870459'))
        with patch(CHECK, _answer('active')):
            pay.action_post()
        self.assertNotEqual(pay.state, 'draft')

    def test_does_not_block_when_arca_is_down(self):
        pay = self._payment(self._partner('30715870459'))
        with patch(CHECK, _answer('error', 'sin conexion')):
            pay.action_post()
        self.assertNotEqual(pay.state, 'draft')
        self.assertIn('No se pudo consultar', ' '.join(pay.message_ids.mapped('body')))

    def test_override_group_can_pay_and_it_is_recorded(self):
        group = self.env.ref('lotoi_arca_check.group_override')
        self.env.user.write({'group_ids': [(4, group.id)]}) if 'group_ids' in self.env.user._fields \
            else self.env.user.write({'groups_id': [(4, group.id)]})
        pay = self._payment(self._partner('20000000117'))
        with patch(CHECK, _answer('inactive')):
            pay.action_post()
        self.assertNotEqual(pay.state, 'draft')
        self.assertIn('Pago autorizado', ' '.join(pay.message_ids.mapped('body')))

    def test_foreign_partner_is_not_checked(self):
        partner = self._partner('218061260016', country_id=self.env.ref('base.uy').id)
        pay = self._payment(partner)
        with patch(CHECK, side_effect=AssertionError('no debe consultar ARCA')):
            pay.action_post()

    def test_switch_off_parameter(self):
        self.env['ir.config_parameter'].sudo().set_param('lotoi_arca_check.enabled', '0')
        pay = self._payment(self._partner('20000000117'))
        with patch(CHECK, side_effect=AssertionError('no debe consultar ARCA')):
            pay.action_post()

    def test_empty_cached_status_is_not_trusted(self):
        """Un resultado guardado sin estado (por ejemplo del boton) no debe saltear la consulta."""
        partner = self._partner('20000000117')
        partner.write({'lotoi_arca_checked_at': self.env.cr.now(), 'lotoi_arca_status': False})
        pay = self._payment(partner)
        with patch(CHECK, _answer('not_found')), self.assertRaises(UserError):
            pay.action_post()
