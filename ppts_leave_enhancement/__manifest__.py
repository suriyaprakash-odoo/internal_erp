# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.
{
    'name' : 'PPTS Leave Enhancement',
    'version': '11.0',
    'author': 'PPTS [India] Pvt.Ltd.',
    'category': 'Leave',
    'website':  'https://www.pptssolutions.com',
    'summary': 'Leave Enhancement',
    'depends': [
        'contacts','hr','hr_holidays','hr_holidays_public','hr_attendance','base'],
    'data': [
        'views/public_holidays_view.xml',
        'views/hr_attendance_view.xml',
        'views/hr_leaves_view.xml',
        
    ],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}