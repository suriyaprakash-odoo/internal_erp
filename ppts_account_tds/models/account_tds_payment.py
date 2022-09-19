# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date

class AccountTdsPayment(models.Model):
    _name = 'account.tds.payment'
    _description = 'Account TDS Payment'        
    
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    payment_id = fields.Many2one('account.payment')
    invoice_id = fields.Many2one('account.invoice')
    invoice_line_id = fields.Many2one('account.invoice.line')
    name = fields.Char('Journal Number')
    code = fields.Char('Code')
    date = fields.Date('Date From')
    tds_deduct = fields.Boolean('Deduct now ?')
    partner_id = fields.Many2one('res.partner',"Partner")
    tds_section_id = fields.Many2one('account.tds',"TDS Section ID")
    account_id = fields.Many2one('account.account', "Account")
    amount = fields.Float('Assesable Amount')
    bal_amount = fields.Float('TDS Balance')
    tds_payable = fields.Float('Payable')
    tds_amount = fields.Float('TDS Total')
    payment_bal_amount = fields.Float('TDS Total')
    tds_amount_residual = fields.Float('TDS Residual')
    tds_payment_line_ids = fields.One2many('account.tds.payment.line','payment_line_id')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open'), ('paid', 'Paid')], string='State', default='draft')
    
class AccountTdsPaymentLine(models.Model):
    _name = 'account.tds.payment.line'
    _description = 'Account TDS Payment Line' 
    
    payment_line_id = fields.Many2one('account.tds.payment')
    tax_type = fields.Selection([('tds', 'TDS'), ('sur', 'Sur')], string='Tax')
    credit = fields.Float('Credit')
    debit = fields.Float('Debit')
    rate = fields.Float('Rate')
    base = fields.Float('Base')
  
class AccountTdsReconcile(models.Model):
    _name = 'account.tds.reconcile'
    _description = 'Account TDS Reconcile'        
    
    invoice_id = fields.Many2one('account.invoice')
    currency_id = fields.Many2one('res.currency',related='invoice_id.currency_id')
    tds_payment_id = fields.Many2one('account.tds.payment')
    name = fields.Char('Journal Number')
    code = fields.Char('Code')
    date = fields.Date('Date From')
    partner_id = fields.Many2one('res.partner',"Partner")
    tds_section_id = fields.Many2one('account.tds',"TDS Section ID")
    account_id = fields.Many2one('account.account', "Account")
    amount = fields.Float('Assesable Amount')
    bal_amount = fields.Float('Balance')
    tds_payable = fields.Float('Payable')
    tds_amount = fields.Float('TDS')
    reconcile_amount = fields.Float('Reconcile')
    reconciled = fields.Float('Reconcile', default=0.0)
    is_reconcile = fields.Boolean(default=False)
    invoice_state = fields.Boolean(default=False,store=True, compute='_compute_state',)
    
    @api.one
    @api.depends('invoice_id.state')
    def _compute_state(self):
        if self.invoice_id.state != 'draft':
            self.invoice_state = True
        
    @api.multi
    def add_tds(self):
        if self.reconcile_amount<=0.0:
            raise UserError(_('Enter a valid amount.'))
        if self.bal_amount<self.reconcile_amount or self.tds_payment_id.bal_amount<self.reconcile_amount:
            raise UserError(_('Enter a valid amount.  Reconcile Value is more than the Balance TDS Amount.'))
        if self.bal_amount <= 0.0:
            raise UserError(_('No TDS balance to deduct/adjust.'))
        if self.tds_payment_id.bal_amount<=0.0:
            raise UserError(_('TDS balance already paid.'))
        else:
            invoice_id = self.env['account.invoice'].search([('id','=', self.invoice_id.id)])
            if invoice_id:
                if invoice_id.amount_tds <= 0 or invoice_id.state!='draft':
                    raise UserError(_('No TDS balance to deduct/adjust.'))
                if invoice_id.amount_tds < self.reconcile_amount:
                    raise UserError(_('Enter a valid amount.  Reconcile Value is more than the Invoice TDS Amount.'))
                else:
                    bal = 0.0
                    reconcile_amount = self.reconcile_amount
                    if invoice_id.amount_tds > self.reconcile_amount:
                        rec_amount = self.reconcile_amount
                        bal = invoice_id.amount_tds - self.reconcile_amount 
                        for line in invoice_id.invoice_line_ids:
                            if line.is_apply:
                                for pay in line.tds_invoice_ids:
                                    if rec_amount > 0:
                                        if pay.bal_amount > rec_amount:
                                            pay.bal_amount = pay.bal_amount - rec_amount
                                            rec_amount = 0.0
                                        if rec_amount > pay.bal_amount:
                                            rec_amount = rec_amount - pay.bal_amount
                                            pay.bal_amount = 0.0
                                        if pay.bal_amount == rec_amount:
                                            rec_amount = 0.0
                                            pay.bal_amount = 0.0
                        invoice_id.amount_tds = bal
                        self.bal_amount = self.bal_amount - self.reconcile_amount
                        self.reconciled = self.reconciled + self.reconcile_amount
                        self.tds_payment_id.bal_amount = self.tds_payment_id.bal_amount - self.reconcile_amount
#                         if self.tds_payment_id.bal_amount == 0.00:
#                             self.tds_payment_id.state = 'paid'
                        self.reconcile_amount = self.bal_amount
                        self.is_reconcile = True
                        self.env['tds.reconciled'].create({
                        'invoice_id': self.invoice_id.id,
                        'tds_payment_id': self.tds_payment_id.id,
                        'tds_reconcile_id': self.id,
                        'partner_id': self.partner_id.id,
                        'name': self.name,
                        'date': date.today(),
                        'reconcile_amount': reconcile_amount,
                            })
                        invoice_id.amount_total = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds 
                        invoice_id.amount_total_company_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.amount_total_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.residual = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.residual_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.is_tds_reconcile = True
                        return True
                    if self.reconcile_amount > invoice_id.amount_tds:
                        rec_amount = self.reconcile_amount
                        for line in invoice_id.invoice_line_ids:
                            if line.is_apply:
                                for pay in line.tds_invoice_ids:
                                    if rec_amount > 0:
                                        if pay.bal_amount > rec_amount:
                                            pay.bal_amount = pay.bal_amount - rec_amount
                                            rec_amount = 0.0
                                        if rec_amount > pay.bal_amount:
                                            rec_amount = rec_amount - pay.bal_amount
                                            pay.bal_amount = 0.0
                                        if pay.bal_amount == rec_amount:
                                            rec_amount = 0.0
                                            pay.bal_amount = 0.0
                        self.bal_amount = self.bal_amount - self.reconcile_amount 
                        self.tds_payment_id.bal_amount = self.tds_payment_id.bal_amount - self.reconcile_amount 
#                         if self.tds_payment_id.bal_amount == 0.00:
#                             self.tds_payment_id.state = 'paid'
                        invoice_id.amount_tds = invoice_id.amount_tds - self.reconcile_amount 
                        self.reconciled = self.reconciled + self.reconcile_amount
                        self.reconcile_amount = self.bal_amount
                        self.is_reconcile = True
                        self.env['tds.reconciled'].create({
                        'invoice_id': self.invoice_id.id,
                        'tds_payment_id': self.tds_payment_id.id,
                        'tds_reconcile_id': self.id,
                        'partner_id': self.partner_id.id,
                        'name': self.name,
                        'date': date.today(),
                        'reconcile_amount': reconcile_amount,
                            })
                        invoice_id.amount_total = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds 
                        invoice_id.amount_total_company_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.amount_total_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.residual = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.residual_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.is_tds_reconcile = True
                        return True
                    if invoice_id.amount_tds == self.reconcile_amount:
                        rec_amount = self.reconcile_amount
                        for line in invoice_id.invoice_line_ids:
                            if line.is_apply:
                                for pay in line.tds_invoice_ids:
                                    if rec_amount > 0:
                                        if pay.bal_amount > rec_amount:
                                            pay.bal_amount = pay.bal_amount - rec_amount
                                            rec_amount = 0.0
                                        if rec_amount > pay.bal_amount:
                                            rec_amount = rec_amount - pay.bal_amount
                                            pay.bal_amount = 0.0
                                        if pay.bal_amount == rec_amount:
                                            rec_amount = 0.0
                                            pay.bal_amount = 0.0
                        self.bal_amount = self.bal_amount - self.reconcile_amount
                        self.tds_payment_id.bal_amount = self.tds_payment_id.bal_amount - self.reconcile_amount
#                         if self.tds_payment_id.bal_amount == 0.00:
#                             self.tds_payment_id.state = 'paid'
                        invoice_id.amount_tds = bal
                        self.reconciled = self.reconciled + self.reconcile_amount
                        self.reconcile_amount = self.bal_amount
                        self.is_reconcile = True
                        self.env['tds.reconciled'].create({
                            'invoice_id': self.invoice_id.id,
                            'tds_payment_id': self.tds_payment_id.id,
                            'tds_reconcile_id': self.id,
                            'partner_id': self.partner_id.id,
                            'name': self.name,
                            'date': date.today(),
                            'reconcile_amount': reconcile_amount,
                        })
                        invoice_id.amount_total = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds 
                        invoice_id.amount_total_company_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.amount_total_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.residual = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.residual_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                        invoice_id.is_tds_reconcile = True
                        return True
                    
    @api.multi
    def unreconcile_tds(self):
        if self.bal_amount == self.tds_amount:
            raise UserError(_('No Reconciliation done earlier.  TDS available to adjust.'))
        else:
            invoice_id = self.env['account.invoice'].search([('id','=', self.invoice_id.id)])
            if invoice_id:
                if invoice_id.amount_tds_residual == invoice_id.amount_tds or invoice_id.state!='draft':
                    raise UserError(_('No Reconciliation done earlier.  TDS available to adjust.'))
                else:
                    if invoice_id.amount_tds_residual > invoice_id.amount_tds:
                        bal2 = self.reconciled
                        bal = invoice_id.amount_tds_residual - invoice_id.amount_tds
                        if bal > self.tds_amount:
                            self.bal_amount = self.tds_amount
                            self.reconciled = 0.0
                            self.reconcile_amount = self.bal_amount
                            self.tds_payment_id.bal_amount = self.tds_amount
                            if self.tds_payment_id.bal_amount != 0.00:
                                self.tds_payment_id.state = 'open'  
                        if bal < self.tds_amount:
                            self.bal_amount = bal + self.bal_amount
                            self.reconciled = 0.0
                            self.reconcile_amount = self.bal_amount
                            self.tds_payment_id.bal_amount = self.tds_payment_id.bal_amount + bal
                            if self.tds_payment_id.bal_amount != 0.00:
                                self.tds_payment_id.state = 'open'
                        if bal == self.tds_amount:
                            self.bal_amount = bal
                            self.reconciled = 0.0
                            self.reconcile_amount = self.bal_amount
                            self.tds_payment_id.bal_amount = bal
                            if self.tds_payment_id.bal_amount != 0.00:
                                self.tds_payment_id.state = 'open'
                        for line in invoice_id.invoice_line_ids:
                            if line.is_apply:
                                for pay in line.tds_invoice_ids:
                                    pay.bal_amount = pay.bal_amount + bal2
                        reconcile_id = self.env['tds.reconciled'].search([('tds_reconcile_id','=',self.id)])
                        for rec in reconcile_id:
                            rec.unlink()
                    invoice_id.amount_total = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds 
                    invoice_id.amount_total_company_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                    invoice_id.amount_total_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                    invoice_id.residual = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                    invoice_id.residual_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
            if invoice_id.amount_tds_residual == invoice_id.amount_tds:
                invoice_id.is_tds_reconcile = False  
                
class TdsReconciled(models.Model):
    _name = 'tds.reconciled'
    _description = 'Account TDS Reconcile'        
    
    invoice_id = fields.Many2one('account.invoice')
    currency_id = fields.Many2one('res.currency',related='invoice_id.currency_id')
    tds_payment_id = fields.Many2one('account.tds.payment')
    tds_reconcile_id = fields.Many2one('account.tds.reconcile')
    partner_id = fields.Many2one('res.partner',"Partner")
    name = fields.Char('Journal Number')
    date = fields.Date('Date From')
    reconcile_amount = fields.Float('TDS')
    
    @api.multi
    def unreconcile_tds(self):
        if self.tds_reconcile_id.bal_amount == self.tds_reconcile_id.tds_amount:
            raise UserError(_('No Reconciliation done earlier.  TDS available to adjust.'))
        else:
            invoice_id = self.env['account.invoice'].search([('id','=', self.invoice_id.id)])
            if invoice_id:
                if invoice_id.amount_tds_residual == invoice_id.amount_tds or invoice_id.state!='draft':
                    raise UserError(_('No Reconciliation done earlier.  TDS available to adjust.'))
                else:
                    if invoice_id.amount_tds_residual > invoice_id.amount_tds:
                        bal2 = self.reconcile_amount
                        self.tds_reconcile_id.bal_amount = self.tds_reconcile_id.bal_amount + self.reconcile_amount
                        self.tds_reconcile_id.reconciled = self.tds_reconcile_id.reconciled - self.reconcile_amount
                        self.tds_reconcile_id.reconcile_amount = self.tds_reconcile_id.bal_amount
                        self.tds_payment_id.bal_amount = self.tds_payment_id.bal_amount + self.reconcile_amount
                        if self.tds_payment_id.bal_amount != 0.00:
                            self.tds_payment_id.state = 'open'
                        for line in invoice_id.invoice_line_ids:
                            if line.is_apply:
                                for pay in line.tds_invoice_ids:
                                    if bal2 > 0:
                                        if pay.tds_amount != pay.bal_amount:
                                            if bal2 == pay.tds_amount:
                                                pay_bal = pay.tds_amount - pay.bal_amount
                                                pay.bal_amount = pay.bal_amount + pay_bal
                                                bal2 = bal2 - pay_bal
                                            if pay.tds_amount > bal2:
                                                pay.bal_amount = pay.bal_amount + bal2
                                                bal2 = 0.0
                                            if bal2 > pay.tds_amount:
                                                pay_bal = pay.tds_amount - pay.bal_amount
                                                bal2 = bal2 - pay_bal
                                                pay.bal_amount = pay.bal_amount + pay_bal
                    invoice_id.amount_total = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds 
                    invoice_id.amount_total_company_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                    invoice_id.amount_total_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                    invoice_id.residual = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
                    invoice_id.residual_signed = invoice_id.amount_untaxed + invoice_id.amount_tax - invoice_id.amount_tds
            if invoice_id.amount_tds_residual == invoice_id.amount_tds:
                invoice_id.is_tds_reconcile = False  
        self.unlink()
        