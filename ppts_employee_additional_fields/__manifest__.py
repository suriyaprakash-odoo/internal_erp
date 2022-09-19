# -*- coding: utf-8 -*-
{
    'name': 'PPTS Employee Additional Fields',
    'category': 'HR',
    'version': '11.0',
    'sequence': 5,
    'summary': 'PPTS HR,Employee Additional Fields',
    "website": "http://www.pptssolutions.com",
    "author": "PPTS [India] Pvt.Ltd.",
    'description': """
    Adding the additional fields in employee,hr modules
    """,
    'depends': ['base', 'hr', 'calendar', 'hr_recruitment', 'ppts_recruitment_enhancement', 'website_hr_recruitment', 'ppts_experience', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template.xml',
        'data/cron.xml',
        'views/employee_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
