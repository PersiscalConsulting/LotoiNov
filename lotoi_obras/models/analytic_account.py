from odoo import _, api, models
from odoo.exceptions import AccessError


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.model_create_multi
    def create(self, vals_list):
        plan = self.env.ref('lotoi_obras.analytic_plan_obras', raise_if_not_found=False)
        if (
            plan
            and not self.env.su
            and not self.env.user.has_group('lotoi_obras.group_obra_manager')
            and any(vals.get('plan_id') == plan.id for vals in vals_list)
        ):
            raise AccessError(_('Solo los gestores de obras pueden crear obras.'))
        return super().create(vals_list)
