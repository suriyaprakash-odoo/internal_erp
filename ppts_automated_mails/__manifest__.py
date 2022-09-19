# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.
{
    'name' : 'PPTS Automated Mails',
    'version': '11.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'appraisal',
    'website':  'https://www.pptssolutions.com',
    'summary': 'Automated Cron',
    'description': """
        Sending mail regarding Birthday,Anniversary,Tenure,Probation Completion and Training Completion notifications to the respective person/department
        """,
    'depends': [
        'contacts','hr','hr_appraisal','base'],
    'data': [
        'data/cron_notification_views.xml',
        'data/mail_template.xml',
    ],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}