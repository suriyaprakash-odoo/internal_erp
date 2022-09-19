# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "CRM fiscal periods ",
    "summary": " ",
    "version": "10.0.1.0.0",
    "website": "https://www.pptssolutions.com",
    "author": "PPTS",
    "depends": ['base','sale','crm','account_accountant'
                ],
    "data": [
            'security/ir.model.access.csv',
            'data/fiscal_periods_cron.xml', 
            'views/fiscal_periods_view.xml',
            'views/fiscal_periods_inherit_view.xml', 
    ],
    'installable' : True,
    'auto_install' : False,
    'application' : True,
}
