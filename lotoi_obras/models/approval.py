from odoo import models


class ApprovalProductLine(models.Model):
    _name = 'approval.product.line'
    _inherit = ['approval.product.line', 'lotoi.obra.mixin']

    # In the approvals the work is only a selector: they do not make journal entries.
    _lotoi_obra_mirror = 'x_studio_reference'
