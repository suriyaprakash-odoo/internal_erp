# Copyright 2017 Eficent Business and IT Consulting Services S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

{
    "name": "PPTS Account Invoice",
    "author": "PPTS [India] Pvt.Ltd.",
    "website": "http://www.pptssolutions.com",
    "version": "11.0.1.0.0",
    "category": "Account Invoice",
    'sequence': 62,
    'summary': 'PPTS Account Invoice',
    'description': "Invoice for Customers",
    "depends": ['base','account'],
    "data": [
        'data/account_account_type.xml',
        'report/account_report.xml',
        'report/report_ppts_invoice.xml',
        'views/ppts_account_invoice_view.xml',
        'wizard/e_brc_wizard_views.xml',
    ],
    "license": 'LGPL-3',
    "installable": True,
    "auto_install": False,
    "application": True,
}
