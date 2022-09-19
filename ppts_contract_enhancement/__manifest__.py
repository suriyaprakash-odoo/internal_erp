# -*- coding: utf-8 -*-
{
    'name': 'PPTS Contract Enhancement',
    'category': 'HR',
    'version': '11.0',
    'sequence': 5,
    'summary': 'PPTS HR,Contract Enhancement',
    'description': """
    """,
    'depends': ['base','hr','hr_contract','calendar','hr_recruitment','ppts_recruitment_enhancement','website_hr_recruitment','ppts_experience'],
    'data': [
        'views/contract_views.xml',
        'views/contract_rule_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
