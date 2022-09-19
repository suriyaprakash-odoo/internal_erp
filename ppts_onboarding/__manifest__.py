# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "PPTS Onboarding",
    "summary": "Onboarding",
    "version": "10.0.1.0.0",
    "category": "Human Resource",
    "website": "http://www.pptssolutions.com",
    "author": "PPTS [India] Pvt.Ltd.",
    "depends": ['base',
                'hr_recruitment',
                'calendar',
                'mail',
                'account',
                'website',
                'website_sign',
                'web_planner',
                'hr_contract',
                'ppts_experience',
                'ppts_recruitment_enhancement',
                'document',
                ],
    "data": [
            'security/onboarding_security.xml',
            'security/ir.model.access.csv',
            'data/mail_template.xml',
            'views/onboarding_views.xml',
            'views/onboarding_config_views.xml',
            'data/web_planner_data.xml',
            
    ],
    'qweb': ['static/xml/web_planner.xml'],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
