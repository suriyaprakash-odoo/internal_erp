# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Customer Type',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'version': '11.0.0',
    'category': 'Sales',
    'sequence': 63,
    'summary': 'Customer Type',
    'description': "Customer Type Master",
    
    'depends': ['base','sale','account'],
    'data': [
            'views/ppts_customer_type_master_views.xml',
            ],
    'license': 'LGPL-3',
    
    'installable': True,
    'auto_install': False,
    'application': True,

}