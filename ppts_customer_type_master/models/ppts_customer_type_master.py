# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError
from docutils.nodes import field

class PptsCustomerTypeMaster(models.Model):
    
    _name = "ppts.customer.type.master"
    _description = "Customer Type"
    _order = 'name'

    name = fields.Char('Name', required=True, index=True, copy=False)
    code = fields.Char('Code')
    active = fields.Boolean('Active',default=True)
    
class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    billing = fields.Boolean(string='Billing')

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    customer_type = fields.Selection([('billing', 'Billing'), ('all', 'All')],string='Customer Type',default='billing')

    @api.onchange('customer_type')
    def onchange_customer_type(self):
        domain = {}
        if self.customer_type == 'billing':
            domain = {'partner_id': [('billing', '=', True),('customer', '=', True)]}
        elif self.customer_type == 'all':
            domain = {'partner_id': [('billing', '=', False),('customer', '=', True)]}
        return {'domain': domain}





