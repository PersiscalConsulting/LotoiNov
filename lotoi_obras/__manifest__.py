{
    'name': 'Lotoi - Obras',
    'version': '19.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Closed list of works (obras) used as the "Referencia" of expenses, purchases and approvals.',
    'description': """
The work code ("Referencia") was typed by hand and came out in several
spellings. This module turns it into a selection of analytic accounts of the
"Obras" plan:

* Only the "Gestor de obras" group can create works.
* Expenses, purchase agreements (and the orders made from them) and the lines
  of the approvals show "Referencia" as a selection, in the same place.
* In expenses and purchases the work chosen fills the analytic distribution
  of the lines, so the P&L can be read by work.
* The old text fields are kept, hidden and in sync, so no data is lost.
    """,
    'author': 'Persiscal',
    'website': 'https://www.persiscal.com',
    'license': 'LGPL-3',
    'depends': [
        'analytic',
        'hr_expense',
        'purchase',
        'purchase_requisition',
        'approvals',
        'lotoi_expense',
        'lotoi_purchase',
        'lotoi_approvals',
    ],
    'data': [
        'security/lotoi_obras_security.xml',
        'data/analytic_plan.xml',
        'views/hr_expense_views.xml',
        'views/purchase_views.xml',
        'views/approval_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
