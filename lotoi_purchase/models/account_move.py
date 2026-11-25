from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    lotoi_fixed_currency_rate = fields.Boolean(
        string='Tipo de cambio fijo',
        copy=False,
        help='El tipo de cambio viene de la orden de compra y no sigue la fecha de la factura.',
    )

    @api.depends('lotoi_fixed_currency_rate')
    def _compute_invoice_currency_rate(self):
        fixed = self.filtered('lotoi_fixed_currency_rate')
        super(AccountMove, self - fixed)._compute_invoice_currency_rate()
