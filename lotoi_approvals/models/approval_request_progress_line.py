from odoo import fields, models


class ApprovalRequestProgressLine(models.Model):
    """Work progress line ("Avance de obra") of an approval request.

    It keeps the technical name and the table of the model created with Odoo
    Studio, so its records are reused when the module is installed.
    """
    _name = 'x_approval_request_line_6a5e3'
    _description = 'Avance de obra'
    _order = 'x_studio_sequence asc, id desc'

    x_studio_sequence = fields.Integer(string='Secuencia', default=10)
    x_name = fields.Char(string='Descripción', required=True, translate=True)
    x_approval_request_id = fields.Many2one(
        'approval.request', string='Solicitud', ondelete='cascade')
    x_studio_currency_id = fields.Many2one(
        'res.currency', string='Currency',
        default=lambda self: self.env.company.currency_id,
    )
    x_studio_destinatario = fields.Many2one('res.partner', string='Destinatario')
    x_studio_fc = fields.Char(string='FC')
    x_studio_forma_de_pago = fields.Selection([
        ('Cheque', 'Cheque'),
        ('Echeq', 'Echeq'),
        ('Transferencia', 'Transferencia'),
    ], string='Forma de Pago')
    x_studio_condicion_de_pago = fields.Selection([
        ('7 días', '7 días'),
        ('15 días', '15 días'),
        ('20 días', '20 días'),
        ('30 días', '30 días'),
        ('45 días', '45 días'),
        ('60 días', '60 días'),
    ], string='Condición De Pago')
    x_studio_importe = fields.Monetary(string='Importe', currency_field='x_studio_currency_id')
    x_studio_liberando = fields.Char(string='Liberando')
    x_studio_acumulando = fields.Char(string='Acumulando')
    x_studio_obra = fields.Char(string='Obra')
    x_studio_archivo = fields.Binary(string='Archivo')
    x_studio_archivo_filename = fields.Char(string='Filename for x_studio_archivo')
