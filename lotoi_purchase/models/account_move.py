from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    lotoi_fixed_currency_rate = fields.Boolean(
        string='Fixed exchange rate',
        copy=False,
        help='The rate comes from the purchase order and must not follow the invoice date.',
    )

    @api.depends('lotoi_fixed_currency_rate')
    def _compute_invoice_currency_rate(self):
        fixed = self.filtered('lotoi_fixed_currency_rate')
        super(AccountMove, self - fixed)._compute_invoice_currency_rate()
