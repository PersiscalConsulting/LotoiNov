from odoo import api, fields, models


class PurchaseRequisition(models.Model):
    _name = 'purchase.requisition'
    _inherit = ['purchase.requisition', 'lotoi.obra.mixin']

    # The standard "reference" is the text Lotoi used for the work code.
    _lotoi_obra_mirror = 'reference'

    @api.onchange('lotoi_obra_id')
    def _onchange_lotoi_obra_id(self):
        for requisition in self:
            if requisition.lotoi_obra_id:
                for line in requisition.line_ids:
                    line.analytic_distribution = requisition._lotoi_obra_merge(
                        line.analytic_distribution, requisition.lotoi_obra_id)

    def write(self, vals):
        res = super().write(vals)
        if vals.get('lotoi_obra_id') and not self.env.context.get('lotoi_skip_obra_analytic'):
            for requisition in self:
                for line in requisition.line_ids:
                    line.analytic_distribution = requisition._lotoi_obra_merge(
                        line.analytic_distribution, requisition.lotoi_obra_id)
        return res


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = ['purchase.order', 'lotoi.obra.mixin']

    # The order takes the work from its agreement, and can be set by hand when
    # there is no agreement.
    lotoi_obra_id = fields.Many2one(
        compute='_compute_lotoi_obra_id', store=True, readonly=False)

    @api.depends('requisition_id.lotoi_obra_id')
    def _compute_lotoi_obra_id(self):
        for order in self:
            order.lotoi_obra_id = order.requisition_id.lotoi_obra_id or order.lotoi_obra_id or False

    @api.onchange('lotoi_obra_id')
    def _onchange_lotoi_obra_id(self):
        for order in self:
            if order.lotoi_obra_id:
                for line in order.order_line:
                    if not line.display_type:
                        line.analytic_distribution = order._lotoi_obra_merge(
                            line.analytic_distribution, order.lotoi_obra_id)

    @api.model_create_multi
    def create(self, vals_list):
        orders = super().create(vals_list)
        if not self.env.context.get('lotoi_skip_obra_analytic'):
            orders._lotoi_apply_obra_to_lines()
        return orders

    def write(self, vals):
        res = super().write(vals)
        if 'lotoi_obra_id' in vals and not self.env.context.get('lotoi_skip_obra_analytic'):
            self._lotoi_apply_obra_to_lines()
        return res

    def _lotoi_apply_obra_to_lines(self):
        for order in self.filtered('lotoi_obra_id'):
            for line in order.order_line.filtered(lambda l: not l.display_type):
                distribution = order._lotoi_obra_merge(line.analytic_distribution, order.lotoi_obra_id)
                if distribution != (line.analytic_distribution or {}):
                    line.analytic_distribution = distribution


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('order_id') and 'analytic_distribution' not in vals and not vals.get('display_type'):
                order = self.env['purchase.order'].browse(vals['order_id'])
                if order.lotoi_obra_id and not self.env.context.get('lotoi_skip_obra_analytic'):
                    vals['analytic_distribution'] = order._lotoi_obra_merge(False, order.lotoi_obra_id)
        return super().create(vals_list)
