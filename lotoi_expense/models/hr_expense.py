from odoo import fields, models


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    # Same technical name and type as the field created with Odoo Studio, so
    # the existing column (and its data) is reused when the module is installed.
    x_studio_reference = fields.Char(string='Reference')

    # Lotoi pays its expenses from the petty cash, not out of the employee's pocket.
    payment_mode = fields.Selection(default='company_account')
