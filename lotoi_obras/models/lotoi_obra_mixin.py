from odoo import api, fields, models


class LotoiObraMixin(models.AbstractModel):
    """Selection of the work ("Referencia") shared by expenses, purchases and approvals.

    The legacy text field of each model is kept in sync with the name of the
    selected work, so the views, related fields and exports that still read it
    keep working.
    """
    _name = 'lotoi.obra.mixin'
    _description = 'Selection of the work (obra)'

    # Name of the legacy Char field kept in sync, set by each model.
    _lotoi_obra_mirror = None

    lotoi_obra_id = fields.Many2one(
        'account.analytic.account',
        string='Referencia',
        index=True,
        domain=lambda self: self._lotoi_obra_domain(),
        help='Obra a la que corresponde. Se elige de la lista de obras.',
    )

    @api.model
    def _lotoi_obra_domain(self):
        plan = self.env.ref('lotoi_obras.analytic_plan_obras', raise_if_not_found=False)
        return [('plan_id', '=', plan.id)] if plan else []

    def _lotoi_obra_merge(self, distribution, obra):
        """Return ``distribution`` with the work as 100% of its plan, keeping the other plans."""
        plan_accounts = set(self.env['account.analytic.account'].with_context(active_test=False).search(
            [('plan_id', '=', obra.plan_id.id)]).ids)
        merged = {
            key: value for key, value in (distribution or {}).items()
            if not plan_accounts.intersection(int(i) for i in str(key).split(',') if i)
        }
        merged[str(obra.id)] = 100.0
        return merged

    def _lotoi_obra_prepare(self, vals):
        """Keep the legacy text in sync when the work is written."""
        if 'lotoi_obra_id' in vals and self._lotoi_obra_mirror and not self.env.context.get('lotoi_skip_obra_sync'):
            obra = self.env['account.analytic.account'].browse(vals['lotoi_obra_id']) if vals['lotoi_obra_id'] else False
            vals[self._lotoi_obra_mirror] = obra.name if obra else False
        return vals

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            self._lotoi_obra_prepare(vals)
        return super().create(vals_list)

    def write(self, vals):
        self._lotoi_obra_prepare(vals)
        return super().write(vals)
