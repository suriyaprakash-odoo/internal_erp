
{
    'name': 'PPTS Overtime Enhancement',
    'summary': 'Overtime Enhancement',
    'version': '11.0',
    'description': """
    Management of overtime taken by the employees.
""",
    'category': 'Human Resources',
    'author': 'PPTS [India] Pvt.Ltd.',
    'website':  'https://www.pptssolutions.com',
    'depends':['hr_contract','hr_attendance','hr','base'],
    'data': [
        'security/ir.model.access.csv',
        'views/bt_hr_overtime_view.xml',
        'views/res_config_settings_view.xml',
        'data/bt_hr_overtime_data.xml'
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}




