# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Account Payment Unadjust Amount',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'version': '11.0.0',
    'sequence': 63,
    'description': "Added unadjust Amount field in account payment tree view.",
    'depends': ['base','account'],
    'data': [     
        'views/account_payment_view.xml',
        ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,

}