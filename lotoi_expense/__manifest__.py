{
    'name': 'Lotoi - Expenses',
    'version': '19.0.1.0.1',
    'category': 'Human Resources/Expenses',
    'summary': 'Replaces the Odoo Studio customizations made on expenses for Lotoi.',
    'description': """
Replaces in code the customizations that Lotoi built with Odoo Studio on the
Expenses app.

* Keeps the ``x_studio_reference`` field (work code of each expense) with the
  same technical name and type, so the data of the migrated database is reused.
* Shows it in the expense form (before the date) and in the list (after the name).
* Makes the tax amount editable and hides the manager field on the form.
    """,
    'author': 'Persiscal',
    'website': 'https://www.persiscal.com',
    'license': 'LGPL-3',
    'depends': ['hr_expense', 'analytic'],
    'data': [
        'views/hr_expense_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
