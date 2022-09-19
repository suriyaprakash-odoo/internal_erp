# -*- coding: utf-8 -*-
{
    'name': "PPTS Journal Round Off",

    'summary': """
        Journal Round Off""",

    'description': """
        Journal Round Off
    """,

    'author': "PPTS",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_view.xml',
        'views/res_config_settings_views.xml',
    ],
    
    'installable': True,
    'application': True,
    'auto_install': False,
}