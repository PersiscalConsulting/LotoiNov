{
    'name': 'Lotoi - Control de proveedores en ARCA',
    'version': '19.0.1.0.2',
    'category': 'Accounting/Localizations',
    'summary': 'Blocks supplier payments when the supplier CUIT is inactive or its constancia failed in ARCA.',
    'description': """
Before confirming a payment to a supplier, consults the constancia de inscripcion
of its CUIT in ARCA (web service ws_sr_constancia_inscripcion) and blocks the
payment if the CUIT is inactive, does not exist or its constancia has errors.

* Uses the ARCA certificate and key already loaded in the company (l10n_ar_edi).
* Keeps the last result in the supplier (status, date and message) and reuses it
  for 24 hours (parameter ``lotoi_arca_check.max_age_hours``).
* If ARCA cannot be reached the payment is NOT blocked (a note is left on it).
* Users of the group "Autorizar pagos a proveedores con CUIT inactivo" can
  confirm anyway; the override is recorded on the payment.
* Can be turned off with the parameter ``lotoi_arca_check.enabled`` = 0.
    """,
    'author': 'Persiscal',
    'website': 'https://www.persiscal.com',
    'license': 'LGPL-3',
    'depends': ['account', 'l10n_ar_edi'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
