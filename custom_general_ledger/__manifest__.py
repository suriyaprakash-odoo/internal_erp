# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'General Ledger Customization',
    'category': 'Account',
    'sequence': 100,
    'website': "http://www.pptssolutions.com",
    'author': "PPTS Pvt. Ltd",
    'summary': 'General Ledger customization',
    'version': '1.0',
    'description': """
        General Ledger customization
        """,
    'depends': ['base','account','account_reports'],
    'data': [
        'wizard/general_ledger_wizard.xml',
        ],
    'installable': True,
    'application': True,
}
