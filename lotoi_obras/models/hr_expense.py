from odoo import api, models


class HrExpense(models.Model):
    _name = 'hr.expense'
    _inherit = ['hr.expense', 'lotoi.obra.mixin']

    _lotoi_obra_mirror = 'x_studio_reference'

    @api.onchange('lotoi_obra_id')
    def _onchange_lotoi_obra_id(self):
        for expense in self:
            if expense.lotoi_obra_id:
                expense.analytic_distribution = expense._lotoi_obra_merge(
                    expense.analytic_distribution, expense.lotoi_obra_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('lotoi_obra_id') and 'analytic_distribution' not in vals and not self.env.context.get('lotoi_skip_obra_analytic'):
                obra = self.env['account.analytic.account'].browse(vals['lotoi_obra_id'])
                vals['analytic_distribution'] = self._lotoi_obra_merge(False, obra)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get('lotoi_obra_id') and 'analytic_distribution' not in vals and not self.env.context.get('lotoi_skip_obra_analytic'):
            obra = self.env['account.analytic.account'].browse(vals['lotoi_obra_id'])
            for expense in self:
                super(HrExpense, expense).write(dict(
                    vals, analytic_distribution=expense._lotoi_obra_merge(expense.analytic_distribution, obra)))
            return True
        return super().write(vals)
