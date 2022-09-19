# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountTds(models.Model):
    _name = 'account.tds'
    _description = 'Account TDS'
    
    code = fields.Char('Code',required=True, size=5)
    return_code = fields.Char('Return Code',required=True, size=5)
    name = fields.Char('Section Name',required=True)
    account_id = fields.Many2one('account.account', "Account", required=True)
    payable_to_id = fields.Many2one('res.partner',"Payable to", domain=[('supplier', '=', True)], required=True)
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id, readonly=True)
    tds_percentage = fields.Float('TDS Percentage', readonly=True, copy=False)
    tds_exempt_limit = fields.Float('TDS Threshold Limit', readonly=True, copy=False)
    sur_percentage = fields.Float('Sur Percentage', readonly=True, copy=False)
    sur_exempt_limit = fields.Float('Sur Expected Limit', readonly=True, copy=False)
    deduct_base = fields.Boolean('Deduct TDS from Base Amount')
    tds_line_ids = fields.One2many('account.tds.line','tds_id')
    
    @api.multi
    def action_change_rate(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        context.update({'act_id':self.id})
        return {
            'name': _('Tax Rates'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.tds.rate',
            'context': context,
            'target': 'new'
        }
    
class AccountTdsLine(models.Model):
    _name = 'account.tds.line'
    _description = 'Account TDS Line'
    
    tds_id = fields.Many2one('account.tds',"TDS")
    date_from = fields.Date('Date Applicable From', readonly=True)
    tds_percentage = fields.Float('TDS Rate', readonly=True)
    tds_exempt_limit = fields.Float('TDS Threshold Limit', readonly=True)
    sur_percentage = fields.Float('Sur Rate', readonly=True)
    sur_exempt_limit = fields.Float('Sur Exempt Limit', readonly=True)
    active_line = fields.Boolean('Active')
    
    @api.multi
    def write(self, vals):
        res = super(AccountTdsLine, self).write(vals)
        if vals.get('active_line'):
            self.tds_id.write({
                'tds_percentage': self.tds_percentage,
                'tds_exempt_limit': self.tds_exempt_limit,
                'sur_percentage': self.sur_percentage,
                'sur_exempt_limit': self.sur_exempt_limit
                })
            tds_line_ids = self.env['account.tds.line'].search([('id', '!=', self.id),('tds_id', '=', self.tds_id.id)])
            for line in tds_line_ids:
                line.active_line = False
        return res
    
class AccountTdsDeducteeType(models.Model):
    _name = 'account.tds.deductee.type'
    _description = 'Account TDS Deductee Type'
    
    name = fields.Many2one('res.partner',"TDS Deductee", domain=[('supplier', '=', True)])
    residential = fields.Boolean('Residential status,Resident?')
    company_id = fields.Many2one('res.company', "Company", default=lambda self: self.env.user.company_id, readonly=True)
    tds_ids = fields.Many2many('account.tds','tds_deductee_type_rel',string="TDS Section")
    active = fields.Boolean(default=True)
    pan_check = fields.Boolean('Check PAN')

    @api.model
    def create(self, vals):
        type_id = self.env['account.tds.deductee.type'].search([('name', '=', vals['name'])])
        if type_id:
            raise UserError(_("This Partner Already Exists."))
        res = super(AccountTdsDeducteeType, self).create(vals)
        res.name.tds_deductee_id = res.id
        return res
     
    @api.multi
    def write(self, vals):
        if vals.get('name'):
            type_id = self.env['account.tds.deductee.type'].search([('name', '=', vals['name'])])
            if type_id:
                raise UserError(_("This Partner Already Exists."))
            partner_id = self.env['res.partner'].search([('tds_deductee_id', '=', self.id)])
            for par in partner_id:
                par.tds_deductee_id = False
                par.tds_section_id = False
        res = super(AccountTdsDeducteeType, self).write(vals)
        self.name.tds_deductee_id = self.id
        return res
    
