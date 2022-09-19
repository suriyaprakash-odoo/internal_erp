# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Custom Employee',
    'version': '1.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'hr',
    'sequence': 5,
    'summary': 'New field will enabled',
    'description': """
    This module enables new fields in the HR module.
""",
    'website': 'https://www.pptssolutions.com',
    'depends': [
        'base','hr','hr_contract','ppts_contract_enhancement',
    ],
    'data': [
        'views/employee_view.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}
