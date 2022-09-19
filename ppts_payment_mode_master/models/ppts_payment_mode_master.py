# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class PptsPaymentModeMaster(models.Model):
    
    _name = "ppts.payment.mode.master"
    _description = "Payment Mode"
    _order = 'name'

    name = fields.Char('Name', required=True, index=True, copy=False)
    code = fields.Char('Code', copy=False)
    active = fields.Boolean('Active',default=True)
    
    