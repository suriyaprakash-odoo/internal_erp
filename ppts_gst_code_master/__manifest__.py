# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'GST Code',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'version': '11.0.0',
    'category': 'Sales',
    'sequence': 63,
    'summary': 'GST Code',
    'description': "GST Code Master",
    
    'depends': ['base','sale','account'],
    'data': [
            'views/ppts_gst_code_master_views.xml',
            ],
    'license': 'LGPL-3',
    
    'installable': True,
    'auto_install': False,
    'application': True,

}