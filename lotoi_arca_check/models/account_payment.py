from odoo import _, models
from odoo.exceptions import UserError

from .res_partner import BLOCKING, STATUS


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _lotoi_arca_is_employee(self, partner):
        """Los reintegros a empleados no se controlan (su CUIL no es el de un proveedor)."""
        employee = self.env.get('hr.employee')
        if employee is None or 'work_contact_id' not in employee._fields:
            return False
        return bool(employee.sudo().search_count([('work_contact_id', '=', partner.id)]))

    def _lotoi_arca_control(self):
        icp = self.env['ir.config_parameter'].sudo()
        if icp.get_param('lotoi_arca_check.enabled', '1') in ('0', 'False', 'false'):
            return
        can_override = self.env.user.has_group('lotoi_arca_check.group_override')
        status_names = dict(STATUS)
        blocked, checked = {}, {}
        for pay in self.filtered(lambda p: p.state == 'draft' and p.payment_type == 'outbound'
                                 and p.partner_type == 'supplier' and p.partner_id):
            partner = pay.partner_id.commercial_partner_id
            if not partner._lotoi_arca_applies() or self._lotoi_arca_is_employee(partner):
                continue
            if partner.id not in checked:
                checked[partner.id] = partner._lotoi_arca_refresh()
            status = checked[partner.id]
            if status in BLOCKING:
                if can_override:
                    pay.message_post(body=_('Pago autorizado a pesar de que ARCA informa: %s (%s).',
                                            status_names[status], partner.lotoi_arca_message or ''))
                else:
                    blocked[partner] = status
            elif status == 'error':
                pay.message_post(body=_('No se pudo consultar el estado del CUIT en ARCA: %s. El pago se confirmó igual.',
                                        partner.lotoi_arca_message or ''))
        if blocked:
            lines = ['- %s (CUIT %s): %s. %s' % (p.name, p.vat, status_names[s], p.lotoi_arca_message or '')
                     for p, s in blocked.items()]
            raise UserError(_(
                'No se puede confirmar el pago porque ARCA informa un problema con el CUIT de:\n%s\n\n'
                'Si corresponde pagar igual, un usuario del grupo "Autorizar pagos a proveedores con CUIT inactivo" '
                'puede confirmarlo.', '\n'.join(lines)))

    def action_post(self):
        self._lotoi_arca_control()
        return super().action_post()
