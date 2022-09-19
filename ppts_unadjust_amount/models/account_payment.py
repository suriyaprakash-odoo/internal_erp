# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_compare

class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    unadjust_amount = fields.Float(string="Unadjust Amount", copy=False)
    
    @api.model
    def create(self, vals):
        vals['unadjust_amount'] = vals['amount']
        return super(AccountPayment, self).create(vals)
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    @api.depends('debit', 'credit', 'amount_currency', 'currency_id', 'matched_debit_ids', 'matched_credit_ids', 'matched_debit_ids.amount', 'matched_credit_ids.amount', 'account_id.currency_id', 'move_id.state')
    def _amount_residual(self):
        """ Computes the residual amount of a move line from a reconciliable account in the company currency and the line's currency.
            This amount will be 0 for fully reconciled lines or lines from a non-reconciliable account, the original line amount
            for unreconciled lines, and something in-between for partially reconciled lines.
        """
        for line in self:
            if not line.account_id.reconcile:
                line.reconciled = False
                line.amount_residual = 0
                line.amount_residual_currency = 0
                continue
            #amounts in the partial reconcile table aren't signed, so we need to use abs()
            amount = abs(line.debit - line.credit)
            amount_residual_currency = abs(line.amount_currency) or 0.0
            sign = 1 if (line.debit - line.credit) > 0 else -1
            if not line.debit and not line.credit and line.amount_currency and line.currency_id:
                #residual for exchange rate entries
                sign = 1 if float_compare(line.amount_currency, 0, precision_rounding=line.currency_id.rounding) == 1 else -1

            for partial_line in (line.matched_debit_ids + line.matched_credit_ids):
                # If line is a credit (sign = -1) we:
                #  - subtract matched_debit_ids (partial_line.credit_move_id == line)
                #  - add matched_credit_ids (partial_line.credit_move_id != line)
                # If line is a debit (sign = 1), do the opposite.
                sign_partial_line = sign if partial_line.credit_move_id == line else (-1 * sign)

                amount += sign_partial_line * partial_line.amount
                #getting the date of the matched item to compute the amount_residual in currency
                if line.currency_id:
                    if partial_line.currency_id and partial_line.currency_id == line.currency_id:
                        amount_residual_currency += sign_partial_line * partial_line.amount_currency
                    else:
                        if line.balance and line.amount_currency:
                            rate = line.amount_currency / line.balance
                        else:
                            date = partial_line.credit_move_id.date if partial_line.debit_move_id == line else partial_line.debit_move_id.date
                            rate = line.currency_id.with_context(date=date).rate
                        amount_residual_currency += sign_partial_line * line.currency_id.round(partial_line.amount * rate)

            #computing the `reconciled` field.
            reconciled = False
            digits_rounding_precision = line.company_id.currency_id.rounding
            if float_is_zero(amount, precision_rounding=digits_rounding_precision):
                if line.currency_id and line.amount_currency:
                    if float_is_zero(amount_residual_currency, precision_rounding=line.currency_id.rounding):
                        reconciled = True
                else:
                    reconciled = True
            line.reconciled = reconciled

            line.amount_residual = line.company_id.currency_id.round(amount * sign)
            line.amount_residual_currency = line.currency_id and line.currency_id.round(amount_residual_currency * sign) or 0.0
            
            if line.payment_id.state == 'posted':
                if line.debit > 0 and line.payment_id:
                    payment_id = self.env['account.payment'].search([('id','=',line.payment_id.id),('payment_type','=','outbound')])
                    if payment_id:
                        if line.amount_residual_currency:
                            payment_id.write({'unadjust_amount' : abs(line.amount_residual_currency)})
                        else:
                            payment_id.write({'unadjust_amount' : abs(line.amount_residual)})
                if line.credit > 0 and line.payment_id:
                    payment_id = self.env['account.payment'].search([('id','=',line.payment_id.id),('payment_type','=','inbound')])
                    if payment_id:
                        if line.amount_residual_currency:
                            payment_id.write({'unadjust_amount' : abs(line.amount_residual_currency)})
                        else:
                            payment_id.write({'unadjust_amount' : abs(line.amount_residual)})
                
                