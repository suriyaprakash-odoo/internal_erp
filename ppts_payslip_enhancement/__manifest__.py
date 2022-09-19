# -*- coding: utf-8 -*-
{
    'name': 'PPTS Payslip Enhancement',
    'category': 'HR',
    'version': '11.0',
    'sequence': 5,
    'summary': 'PPTS HR,Payslip Enhancement',
    "website": "http://www.pptssolutions.com",
    "author": "PPTS [India] Pvt.Ltd.",
    'description': """
    """,
    'depends': ['hr_payroll','hr_attendance'],
    'data': [
        'views/employee_view.xml',
        'report/report_payslip_templates.xml',
        'report/hr_payroll_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
