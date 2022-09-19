from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountAccount(models.Model):
    _inherit = "account.account"
    
    credit_amount = fields.Float("Credit", readonly=True, compute="_compute_bal")
    debit_amount = fields.Float("Debit", readonly=True, compute="_compute_bal")
    balance_amount = fields.Float("Balance", readonly=True, compute="_compute_bal")
    currency_balance_amount = fields.Monetary('Currency Balance', readonly=True, compute="_compute_bal")
    
    @api.multi
    def _compute_bal(self):
        for acc in self:
            credit = debit = cur_credit = cur_debit = 0.00
            move_id = self.env['account.move.line'].search([('account_id', '=', acc.id)])
            for val in  move_id:
                credit += val.credit
                debit += val.debit
                if val.credit > 0:
                    cur_credit += abs(val.amount_currency)
                if val.debit > 0:
                    cur_debit += abs(val.amount_currency)
            acc.update({
                'credit_amount': credit,
                'debit_amount': debit,
                'balance_amount': debit-credit,
                'currency_balance_amount': cur_debit-cur_credit,
                })
            
            
class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    cash_control = fields.Boolean('Cash/Bank Balance Control', default=False)
    
class VendorMultiPayment(models.Model):
    _inherit = "vendor.multi.payment"
    
    balance_amount = fields.Float("Balance", default = 0.00, readonly = True, compute="_compute_payment_currency_id")
    currency_balance_amount = fields.Monetary('Currency Balance', default = 0.00, readonly = True, compute="_compute_payment_currency_id")
    is_company_currency = fields.Boolean(default=True, compute="_compute_payment_currency_id")
    
    @api.multi
    @api.depends('currency_id')
    def _compute_payment_currency_id(self):
        self.balance_amount = self.journal_id.default_credit_account_id.balance_amount
        self.currency_balance_amount = self.journal_id.default_credit_account_id.currency_balance_amount  
        if self.currency_id.id == self.env.user.company_id.currency_id.id:
            self.is_company_currency = False
        else:
            self.is_company_currency = True
            
    @api.multi
    def create_payments(self):
        if self.journal_id.cash_control:
            if self.currency_id.id == self.env.user.company_id.currency_id.id:
                if self.paid_amount > self.balance_amount:
                    raise UserError(_("Insufficient Balance in Account."))
            else:
                if self.paid_amount > self.currency_balance_amount:
                    raise UserError(_("Insufficient Balance in Account."))
        return super(VendorMultiPayment, self).create_payments()


class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    balance_amount = fields.Float("Balance", default = 0.00, readonly = True, compute="_compute_payment_currency_id")
    currency_balance_amount = fields.Monetary('Currency Balance', default = 0.00, readonly = True, compute="_compute_payment_currency_id")
    is_company_currency = fields.Boolean(default=True, compute="_compute_payment_currency_id")
    
    @api.multi
    @api.depends('currency_id','journal_id')
    def _compute_payment_currency_id(self):
        self.balance_amount = self.journal_id.default_credit_account_id.balance_amount
        self.currency_balance_amount = self.journal_id.default_credit_account_id.currency_balance_amount  
        if self.currency_id.id == self.env.user.company_id.currency_id.id:
            self.is_company_currency = False
        else:
            self.is_company_currency = True
             
    @api.multi
    def post(self):
        if self.journal_id.cash_control:
            if self.currency_id.id == self.env.user.company_id.currency_id.id:
                if self.amount > self.balance_amount:
                    raise UserError(_("Insufficient Balance in Account."))
            else:
                if self.amount > self.currency_balance_amount:
                    raise UserError(_("Insufficient Balance in Account."))
        return super(AccountPayment, self).post()  
        
    