{
    'name': 'Lotoi - Accounting',
    'version': '19.0.1.1.0',
    'category': 'Accounting',
    'summary': 'Lotoi week numbering on invoices and expense account per vendor.',
    'description': """
Adds to invoices and bills the week number Lotoi uses to follow its work: weeks
run from Saturday to Friday and week 1 is the one that contains January 1st.
The week is taken from the invoice date, and can be searched and grouped from
the invoice lists.
    """,
    'author': 'Persiscal',
    'website': 'https://www.persiscal.com',
    'license': 'LGPL-3',
    'depends': ['account'],
    'data': [
        'views/account_move_views.xml',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
