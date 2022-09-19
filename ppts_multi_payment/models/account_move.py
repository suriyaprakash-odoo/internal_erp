from odoo import fields, models, api
from odoo.exceptions import ValidationError

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    customer_cr_partial_id = fields.Many2one("customer.multi.payment.credit.line")
    customer_de_partial_id = fields.Many2one("customer.multi.payment.debit.line")
    vendor_cr_partial_id = fields.Many2one("vendor.multi.payment.credit.line")
    vendor_de_partial_id = fields.Many2one("vendor.multi.payment.debit.line")
    
    def auto_reconcile_lines(self, invoice_type=False, invoice=None):
        if not self.ids:
            return self
        sm_debit_move, sm_credit_move = self._get_pair_to_reconcile()
        if not sm_credit_move or not sm_debit_move:
            return self

        field = self[0].account_id.currency_id and 'amount_residual_currency' or 'amount_residual'
        if not sm_debit_move.debit and not sm_debit_move.credit:
            field = 'amount_residual_currency'
        if self[0].currency_id and all([x.currency_id == self[0].currency_id for x in self]):
            field = 'amount_residual_currency'
        if self._context.get('skip_full_reconcile_check') == 'amount_currency_excluded':
            field = 'amount_residual'
        elif self._context.get('skip_full_reconcile_check') == 'amount_currency_only':
            field = 'amount_residual_currency'
        amount_reconcile = min(sm_debit_move[field], -sm_credit_move[field])
        if amount_reconcile == sm_debit_move[field]:
            self -= sm_debit_move
        if amount_reconcile == -sm_credit_move[field]:
            self -= sm_credit_move
        currency = False
        amount_reconcile_currency = 0
        if sm_debit_move.currency_id == sm_credit_move.currency_id and sm_debit_move.currency_id.id:
            currency = sm_credit_move.currency_id.id
            amount_reconcile_currency = min(sm_debit_move.amount_residual_currency, -sm_credit_move.amount_residual_currency)
        amount_reconcile = min(sm_debit_move.amount_residual, -sm_credit_move.amount_residual)
        amount_to_reconcile = 0
        
        if sm_debit_move.customer_cr_partial_id and sm_credit_move.customer_de_partial_id:
            if sm_debit_move.customer_cr_partial_id.amount_reconcile == sm_credit_move.customer_de_partial_id.amount_reconcile: 
                amount_to_reconcile += sm_debit_move.customer_cr_partial_id.amount_reconcile
                sm_debit_move.customer_cr_partial_id.amount_reconcile -= sm_debit_move.customer_cr_partial_id.amount_reconcile
                sm_credit_move.customer_de_partial_id.amount_reconcile -= sm_credit_move.customer_de_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
            if sm_debit_move.customer_cr_partial_id.amount_reconcile > sm_credit_move.customer_de_partial_id.amount_reconcile:
                amount_to_reconcile += sm_credit_move.customer_de_partial_id.amount_reconcile
                sm_debit_move.customer_cr_partial_id.amount_reconcile -= sm_credit_move.customer_de_partial_id.amount_reconcile
                sm_credit_move.customer_de_partial_id.amount_reconcile -= sm_credit_move.customer_de_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
            if sm_debit_move.customer_cr_partial_id.amount_reconcile < sm_credit_move.customer_de_partial_id.amount_reconcile: 
                amount_to_reconcile += sm_debit_move.customer_cr_partial_id.amount_reconcile
                sm_credit_move.customer_de_partial_id.amount_reconcile -= sm_debit_move.customer_cr_partial_id.amount_reconcile
                sm_debit_move.customer_cr_partial_id.amount_reconcile -= sm_debit_move.customer_cr_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
                
        if sm_debit_move.vendor_cr_partial_id and sm_credit_move.vendor_de_partial_id:
            if sm_debit_move.vendor_cr_partial_id.amount_reconcile == sm_credit_move.vendor_de_partial_id.amount_reconcile: 
                amount_to_reconcile += sm_debit_move.vendor_cr_partial_id.amount_reconcile
                sm_debit_move.vendor_cr_partial_id.amount_reconcile -= sm_debit_move.vendor_cr_partial_id.amount_reconcile
                sm_credit_move.vendor_de_partial_id.amount_reconcile -= sm_credit_move.vendor_de_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
            if sm_debit_move.vendor_cr_partial_id.amount_reconcile > sm_credit_move.vendor_de_partial_id.amount_reconcile:
                amount_to_reconcile += sm_credit_move.vendor_de_partial_id.amount_reconcile
                sm_debit_move.vendor_cr_partial_id.amount_reconcile -= sm_credit_move.vendor_de_partial_id.amount_reconcile
                sm_credit_move.vendor_de_partial_id.amount_reconcile -= sm_credit_move.vendor_de_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
            if sm_debit_move.vendor_cr_partial_id.amount_reconcile < sm_credit_move.vendor_de_partial_id.amount_reconcile: 
                amount_to_reconcile += sm_debit_move.vendor_cr_partial_id.amount_reconcile
                sm_credit_move.vendor_de_partial_id.amount_reconcile -= sm_debit_move.vendor_cr_partial_id.amount_reconcile
                sm_debit_move.vendor_cr_partial_id.amount_reconcile -= sm_debit_move.vendor_cr_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
                
        if sm_debit_move.customer_cr_partial_id and not sm_credit_move.customer_de_partial_id:
            if sm_debit_move.customer_cr_partial_id.amount_reconcile == sm_credit_move.credit: 
                amount_to_reconcile += sm_debit_move.customer_cr_partial_id.amount_reconcile
                sm_debit_move.customer_cr_partial_id.amount_reconcile -= sm_debit_move.customer_cr_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
            if sm_debit_move.customer_cr_partial_id.amount_reconcile > sm_credit_move.credit:
                amount_to_reconcile += sm_credit_move.credit
                sm_debit_move.customer_cr_partial_id.amount_reconcile -= sm_credit_move.credit
                amount_reconcile = amount_to_reconcile
            if sm_debit_move.customer_cr_partial_id.amount_reconcile < sm_credit_move.credit: 
                amount_to_reconcile += sm_debit_move.customer_cr_partial_id.amount_reconcile
                sm_debit_move.customer_cr_partial_id.amount_reconcile -= sm_debit_move.customer_cr_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
                
        if not sm_debit_move.vendor_cr_partial_id and sm_credit_move.vendor_de_partial_id:
            if sm_debit_move.debit == sm_credit_move.vendor_de_partial_id.amount_reconcile: 
                amount_to_reconcile += sm_credit_move.vendor_de_partial_id.amount_reconcile
                sm_credit_move.vendor_de_partial_id.amount_reconcile -= sm_credit_move.vendor_de_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
            if sm_debit_move.debit > sm_credit_move.vendor_de_partial_id.amount_reconcile:
                amount_to_reconcile += sm_credit_move.vendor_de_partial_id.amount_reconcile
                sm_credit_move.vendor_de_partial_id.amount_reconcile -= sm_credit_move.vendor_de_partial_id.amount_reconcile
                amount_reconcile = amount_to_reconcile
            if sm_debit_move.debit < sm_credit_move.vendor_de_partial_id.amount_reconcile: 
                amount_to_reconcile += sm_debit_move.debit
                sm_credit_move.vendor_de_partial_id.amount_reconcile -= sm_debit_move.debit
                amount_reconcile = amount_to_reconcile
                
        sm_debit_move.customer_cr_partial_id = False
        sm_credit_move.customer_de_partial_id = False
        sm_debit_move.vendor_cr_partial_id = False
        sm_credit_move.vendor_de_partial_id = False
        
        if sm_debit_move.currency_id == sm_credit_move.currency_id and sm_debit_move.currency_id.id:
            amount_reconcile_currency = amount_to_reconcile
            
        if self._context.get('skip_full_reconcile_check') == 'amount_currency_excluded':
            amount_reconcile_currency = 0.0
            currency = self._context.get('manual_full_reconcile_currency')
        elif self._context.get('skip_full_reconcile_check') == 'amount_currency_only':
            currency = self._context.get('manual_full_reconcile_currency')
        self.env['account.partial.reconcile'].create({
            'debit_move_id': sm_debit_move.id,
            'credit_move_id': sm_credit_move.id,
            'amount': amount_reconcile,
            'amount_currency': amount_reconcile_currency,
            'currency_id': currency,
        })
        return self.auto_reconcile_lines()
    
    @api.multi
    @api.constrains('amount_currency')
    def _check_currency_amount(self):
        for line in self:
            if not line.payment_id.ven_multi_pay_id and not line.payment_id.cus_multi_pay_id:
                if line.amount_currency:
                    if (line.amount_currency > 0.0 and line.credit > 0.0) or (line.amount_currency < 0.0 and line.debit > 0.0):
                        raise ValidationError(_('The amount expressed in the secondary currency must be positive when account is debited and negative when account is credited.'))
