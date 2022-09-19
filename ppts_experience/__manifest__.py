# -*- coding: utf-8 -*-
{
    'name': 'PPTS Experience',
    'category': 'HR',
    'version': '11.0',
    'sequence': 5,
    'summary': 'PPTS HR,Employee',
    "website": "http://www.pptssolutions.com",
    "author": "PPTS [India] Pvt.Ltd.",
    'description': """
    """,
    'depends': ['hr','hr_recruitment','website_hr_recruitment','website_form_recaptcha','website','portal','survey'],
    'data': [
        # 'security/ir.model.access.csv',
        'data/website_config.xml',
        'views/applicant_view.xml',
        'views/employee_views.xml',
        'views/experience_view.xml',
        'views/recruitment_template.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
