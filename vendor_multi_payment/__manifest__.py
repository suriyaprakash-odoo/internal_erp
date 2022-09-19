{
    'name': 'Vendor Bill Multi Payments',
    'version': '11.0.1.0.0',
    'description': 'Bulk payments for vendor bills',
    'summary': 'Bulk payments for vendor bills',
    'category': 'Account Invoice',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website': "http://www.pptssolutions.com",
    'sequence': 10,
    'depends': ['base','account','ppts_payment_mode_master','mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/vendor_payment_view.xml',
        'wizard/vendor_payment_wizard.xml'
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
