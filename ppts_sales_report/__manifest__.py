# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'PPTS Sales Report',
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    'version': '11.0.0',
    'category': 'Accounting',
    'sequence': 10,
    'summary': 'Accounting Sale Report',
    'description': "Accounting Sale Report",
    
    'depends': ['base','account','website'],
    'data': [
            'wizard/ppts_sale_report_view.xml',
            'views/ppts_sale_report_menu.xml',
            'views/report_web_template.xml',
            ],
    'license': 'LGPL-3',
    
    'installable': True,
    'auto_install': False,
    'application': True,

}