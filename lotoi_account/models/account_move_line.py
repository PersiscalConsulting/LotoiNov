from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _compute_account_id(self):
        super()._compute_account_id()
        # A bill line without product takes the expense account of the vendor.
        # With a product, the account of the product (standard) is kept. The
        # compute only runs when the product, the vendor or the document change,
        # so an account chosen by hand is not overwritten when saving.
        for line in self:
            move = line.move_id
            if (
                line.display_type != 'product'
                or line.product_id
                or not move.is_purchase_document(include_receipts=True)
            ):
                continue
            partner = move.partner_id.commercial_partner_id
            account = partner.with_company(line.company_id).lotoi_expense_account_id
            if account:
                line.account_id = account
