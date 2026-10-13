from odoo import fields, models

PAYMENT_METHODS = [
    ('Transferencia', 'Transferencia'),
    ('Echeq', 'Echeq'),
    ('Efectivo', 'Efectivo'),
    ('Cheque', 'Cheque'),
]
PAYMENT_TERMS = [
    ('Contado', 'Contado'),
    ('7 días', '7 días'),
    ('15 días', '15 días'),
    ('21 días', '21 días'),
    ('30 días', '30 días'),
    ('45 días', '45 días'),
    ('60 días', '60 días'),
]


class ApprovalProductLine(models.Model):
    """Lines of the request, extended with the payment data Lotoi uses.

    The technical names are the ones Odoo Studio generated, so the existing
    columns (and their data) are reused when the module is installed.
    """
    _inherit = 'approval.product.line'

    x_studio_currency_id = fields.Many2one(
        'res.currency', string='Moneda',
        default=lambda self: self.env.company.currency_id,
    )
    x_studio_importe = fields.Monetary(string='Importe', currency_field='x_studio_currency_id')
    x_studio_importe_1 = fields.Monetary(string='Importe', currency_field='x_studio_currency_id')
    x_studio_importe_2 = fields.Monetary(string='Importe', currency_field='x_studio_currency_id')
    x_studio_many2one_field_858_1js9r52nm = fields.Many2one('res.partner', string='Nombre')
    x_studio_many2one_field_2l3_1jspljlkj = fields.Many2one('hr.employee', string='Empleado')
    x_studio_empleado = fields.Many2one('hr.employee', string='Empleado')
    x_studio_many2one_field_6bn_1jv4afmc8 = fields.Many2one('account.tax', string='Impuestos')
    x_studio_n_fc = fields.Char(string='N° FC')
    x_studio_medio_de_pago = fields.Selection(PAYMENT_METHODS, string='Medio De Pago')
    x_studio_condicion_de_pago = fields.Selection(PAYMENT_TERMS, string='Condición De Pago')
    x_studio_reference = fields.Char(string='Reference')
    x_studio_referencia = fields.Char(string='Obra')
    x_studio_archivo = fields.Binary(string='Archivo')
    x_studio_archivo_filename = fields.Char(string='Filename for x_studio_archivo')
    x_studio_binary_field_3vq_1jrvi4piv = fields.Binary(string='Archivo')
    x_studio_binary_field_3vq_1jrvi4piv_filename = fields.Char(
        string='Filename for x_studio_binary_field_3vq_1jrvi4piv')
    x_studio_cbu = fields.Binary(string='CBU')
    x_studio_cbu_filename = fields.Char(string='Filename for x_studio_cbu')
    x_studio_cantidad_de_cuotas_1 = fields.Integer(string='Cantidad cuotas')
    x_studio_ultimo_adelantoprestamo = fields.Date(string='Ultimo Adelanto/Prestamo')
