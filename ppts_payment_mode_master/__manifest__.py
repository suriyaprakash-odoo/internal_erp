# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Payment Mode',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'version': '11.0.0',
    'category': 'Sales',
    'sequence': 63,
    'summary': 'Payment Mode',
    'description': "Payment Mode Master",
    
    'depends': ['base','sale'],
    'data': [
            'security/ir.model.access.csv',
            'views/ppts_payment_mode_master_views.xml',
            ],
    'license': 'LGPL-3',
    
    'installable': True,
    'auto_install': False,
    'application': True,

}