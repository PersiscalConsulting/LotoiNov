from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _lotoi_vendor_expense_account(self):
        """Expense account of the vendor for a bill line without product, else empty."""
        self.ensure_one()
        move = self.move_id
        if (
            self.product_id
            or self.display_type not in (False, 'product')
            or not move.is_purchase_document(include_receipts=True)
        ):
            return self.env['account.account']
        partner = (self.partner_id or move.partner_id).commercial_partner_id
        return partner.with_company(self.company_id).lotoi_expense_account_id

    def _compute_account_id(self):
        super()._compute_account_id()
        # A bill line without product takes the expense account of the vendor.
        # With a product, the account of the product (standard) is kept.
        for line in self:
            account = line._lotoi_vendor_expense_account()
            if account:
                line.account_id = account

    @api.onchange('partner_id')
    def _inverse_partner_id(self):
        super()._inverse_partner_id()
        # Odoo only recomputes the account of the payment term lines when the
        # vendor changes: do it also for the lines without product, when the new
        # vendor has an expense account.
        self._conditional_add_to_compute(
            'account_id',
            lambda line: bool(line._lotoi_vendor_expense_account()),
        )
