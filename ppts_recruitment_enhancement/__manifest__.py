# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": " PPTS Recruitment Enhancement",
    "summary": "Recruitment Enhancement",
    'description': """
          Employee Recruitment process  with customization 
        """,
    "version": "11.0",
    "category": "HR",
    "website": "http://www.pptssolutions.com",
    "author": "PPTS [India] Pvt.Ltd.",
    "depends": ['base','hr_recruitment','mail' ,'survey','hr_recruitment_survey','website_hr_recruitment','ppts_experience'],
    "data": [
            'security/approval_security.xml',
            'security/ir.model.access.csv',
            'data/mail_template_data.xml',
            'data/send_mail_applicant_template.xml',
            'data/hr_recruitment_stages_demo.xml',
            'wizard/refuse_reason_wizard_view.xml',
            'views/recruitment_job_template_view.xml',
            'views/recruitment_menus.xml',
            'views/hr_applicant_view.xml',
            'views/recruitment_template.xml',
            'views/ppts_hr_views.xml',
            'views/ppts_hr_recruitment_view.xml',
            'views/recruitment_extend_seq.xml',
            'views/qualification_skills_form_view.xml',
            'views/mprf_request_views.xml',            
    ],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
