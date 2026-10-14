{
    'name': 'Lotoi - Approvals',
    'version': '19.0.1.0.1',
    'category': 'Human Resources/Approvals',
    'summary': 'Replaces the Odoo Studio customizations made on approvals for Lotoi.',
    'description': """
Replaces in code the customizations that Lotoi built with Odoo Studio on the
Approvals app.

* Payment detail tables on the request (reimbursements, advances and work progress).
* "Avance de obra" lines (own model, same table as the one created with Studio).
* Automation: total amount of the request (sum of the detail lines).
* "Pago" button: sends the receipts to the requester and marks the request as paid.

All technical names (``x_studio_*``) are kept so the data of the migrated
database is reused.
    """,
    'author': 'Persiscal',
    'website': 'https://www.persiscal.com',
    'license': 'LGPL-3',
    'depends': ['approvals', 'approvals_purchase', 'hr', 'account', 'mail'],
    'data': [
        'security/ir_model_access.xml',
        'views/approval_request_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
