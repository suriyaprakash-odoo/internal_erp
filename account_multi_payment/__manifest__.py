{
    'name': 'Account Multi Payments',
    'version': '11.0.1.0.0',
    'description': 'Bulk payments for invoice',
    'summary': 'Bulk payments for invoice',
    'category': 'Account Invoice',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': "http://www.pptssolutions.com",
    'sequence': 10,
    'depends': ['base','account','ppts_payment_mode_master','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_payment_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
