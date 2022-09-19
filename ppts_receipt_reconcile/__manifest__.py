{
    'name': 'Receipt Reconcile',
    'version': '11.0.1.0.0',
    'description': 'Receipt Reconcile',
    'summary': 'Receipt Reconcile',
    'category': 'Account Invoice',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': "http://www.pptssolutions.com",
    'sequence': 10,
    'depends': ['base','account','ppts_payment_mode_master'],
    'data': [
        'views/receipt_reconcile_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
