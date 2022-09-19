# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError

class PptsGstCodeMaster(models.Model):
    
    _name = "ppts.gst.code.master"
    _description = "GST Code"
    _order = 'name'

    name = fields.Char('Name', required=True, index=True, copy=False,size=10)
    code = fields.Char('Code')
    active = fields.Boolean('Active',default=True)
    
    