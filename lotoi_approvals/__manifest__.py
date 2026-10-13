{
    'name': 'Lotoi - Approvals',
    'version': '19.0.1.0.0',
    'category': 'Human Resources/Approvals',
    'summary': 'Replaces the Odoo Studio customizations made on approvals for Lotoi.',
    'description': """
Replaces in code the customizations that Lotoi built with Odoo Studio on the
Approvals app.

* Payment detail tables on the request (reimbursements, advances and work progress).
* "Avance de obra" lines (own model, same table as the one created with Studio).
* Automations: total amount, approver removal for requests coming from a purchase
  order, notification to the approver on employee reimbursements.
* "Pago" button: sends the receipts to the requester and marks the request as paid.

All technical names (``x_studio_*``) are kept so the data of the migrated
database is reused.
    """,
    'author': 'Persiscal',
    'website': 'https://www.persiscal.com',
    'license': 'LGPL-3',
    'depends': ['approvals', 'hr', 'account', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/approval_request_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
