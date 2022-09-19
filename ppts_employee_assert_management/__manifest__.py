# -*- coding: utf-8 -*-
{
    'name': 'PPTS Employee Assert Management',
    'category': 'HR',
    'version': '11.0',
    'sequence': 5,
    'summary': 'PPTS HR,Employee',
    "website": "http://www.pptssolutions.com",
    "author": "PPTS [India] Pvt.Ltd.",
    'description': """
    """,
    'depends': ['hr','hr_recruitment','website_hr_recruitment'],
    'data': [
        'views/employee_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
