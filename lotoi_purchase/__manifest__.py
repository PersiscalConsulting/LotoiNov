{
    'name': 'Lotoi - Purchase',
    'version': '19.0.1.1.0',
    'category': 'Inventory/Purchase',
    'summary': 'Replaces the Odoo Studio customizations made on purchases for Lotoi.',
    'description': """
Replaces in code the customizations that Lotoi built with Odoo Studio on the
Purchase and Purchase Agreements (contratos de compra) apps.

* Purchase agreement: work (obra), sector, priority, delivery date and unit
  of each line.
* Purchase order: reference of the agreement and unit of each line.
* Purchase order: exchange rate that can be fixed for a single order; the bills
  made from it keep that rate.

All technical names (``x_studio_*``) are kept so the data of the migrated
database is reused.
    """,
    'author': 'Persiscal',
    'website': 'https://www.persiscal.com',
    'license': 'LGPL-3',
    'depends': ['purchase', 'purchase_stock', 'purchase_requisition', 'purchase_requisition_stock', 'uom'],
    'data': [
        'views/purchase_views.xml',
        'views/purchase_exchange_rate_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
