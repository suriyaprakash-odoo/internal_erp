# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Partner Ledger Customization',
    'category': 'Account',
    'sequence': 100,
    'website': "http://www.pptssolutions.com",
    'author': "PPTS Pvt. Ltd",
    'summary': 'Partner Ledger customization',
    'version': '1.0',
    'description': """
        Partner Ledger customization
        """,
    'depends': ['base','account','account_reports'],
    'data': [
        'wizard/partner_ledger_view.xml',
        # 'views/views_origin.xml',
        # 'views/sale_config_settings.xml',
        ],
    'installable': True,
    'application': True,
}
