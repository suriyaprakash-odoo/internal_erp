# -*- coding: utf-8 -*-
# Ã‚Â© 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "CRM dashboard",
    "summary": "CRM dashboard",
    "version": "10.0.6",
    "category": "Uncategorized",
    "website": "https://www.pptssolutions.com",
    "author": "PPTS",
    "depends": ['base','web','crm'],
    "data": [
            'security/dashboard_security.xml',
            'security/ir.model.access.csv',
            'views/dashboard_view.xml',
            'views/menuitems.xml',
            'dashboard_script.xml',
    ],
    'qweb': ['static/xml/dashboard.xml',
            ],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
