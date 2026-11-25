from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    lotoi_expense_account_id = fields.Many2one(
        'account.account',
        string='Cuenta de gasto',
        company_dependent=True,
        domain="[('account_type', 'in', ('expense', 'expense_direct_cost', 'expense_depreciation'))]",
        help='Cuenta contable que se usa en las líneas de las facturas de este proveedor '
             'que no tienen producto. Si la línea tiene producto, se usa la cuenta del producto.',
    )
