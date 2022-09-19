# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 NovaPoint Group LLC (<http://www.novapointgroup.com>)
#    Copyright (C) 2004-2010 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
{
    'name': 'CRM Nurture',
    'version': '1.0',
    'category': 'CRM',
    'description': """
    """,
    'author': 'PPTS',
    'depends': ['base', 'crm', 'mail','mail_tracking'],
    'data': [
        "security/ir.model.access.csv",
        "wizard/crm_set_campaign_view.xml",
        "wizard/partner_set_campaign_view.xml",
        "views/crm_nurture.xml",
        "views/res_partner_view.xml",
        "views/crm_lead_view.xml",
        "views/mail_template.xml",
        'data/crm_campaign_demo.xml',
    ],
    'application': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
