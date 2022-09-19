# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.
{
    'name' : 'PPTS Appraisal Enhancement',
    'version': '11.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'appraisal',
    'website':  'https://www.pptssolutions.com',
    'summary': 'Appraisal Enhancement',
    'description': """
        Employee appraisal approval customization
        """,
    'depends': [
        'contacts','hr','hr_appraisal','base'],
    'data': [
        'view/employee_enhancement_view.xml',
    ],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}