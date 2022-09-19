# -*- coding: utf-8 -*-

from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import fields, models, api, _
from odoo.tools import float_is_zero, float_compare
from odoo.addons import decimal_precision as dp


class ResCompany(models.Model):
    _inherit = 'res.company'

    exchange_account_type = fields.Selection([('journal','Based on Journal'),('account','Based on Direct Account')], string='Account Type',default='journal')
    debit_account_id = fields.Many2one('account.account', string='Gain Exchange Rate Account')
    credit_account_id = fields.Many2one('account.account', string='Loss Exchange Rate Account')
    partial_payment = fields.Boolean(string='Create Journal Entry for Partial Payment')

class for_ex_gain_loss(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # round_off = fields.Boolean(string='Allow rounding of invoice amount', help="Allow rounding of invoice amount")
    # round_off_account = fields.Many2one('account.account', string='Round Off Account')
    exchange_account_type = fields.Selection(related="company_id.exchange_account_type", string='Account Type')
    debit_account_id = fields.Many2one('account.account',related="company_id.debit_account_id", string='Gain Exchange Rate Account')
    credit_account_id = fields.Many2one('account.account',related="company_id.credit_account_id", string='Loss Exchange Rate Account')
    partial_payment = fields.Boolean(related="company_id.partial_payment", string='Create Journal Entry for Partial Payment')

    @api.onchange('exchange_account_type')
    def onchange_account_id(self):
        if self.exchange_account_type and self.exchange_account_type == 'journal':
            self.debit_account_id = ''
            self.credit_account_id = ''

    # def set_values(self):
    #     super(for_ex_gain_loss, self).set_values()
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     ICPSudo.set_param('account.exchange_account_type', self.exchange_account_type)
    #     ICPSudo.set_param('account.debit_account_id', self.debit_account_id.id)
    #     ICPSudo.set_param('account.credit_account_id', self.credit_account_id.id)

    #To get values from respected model #
    # @api.model
    # def get_values(self):
    #     res = super(for_ex_gain_loss, self).get_values()
    #     ICPSudo = self.env['ir.config_parameter'].sudo()
    #     res.update(
    #         # exchange_account_type=ICPSudo.get_param('account.exchange_account_type'),debit_account_id=ICPSudo.get_param('account.debit_account_id'),credit_account_id=ICPSudo.get_param('account.credit_account_id')
    #         exchange_account_type=ICPSudo.get_param('account.exchange_account_type')
    #     )
    #     # res.update(
    #     #     debit_account_id=ICPSudo.get_param('account.debit_account_id')
    #     # )
    #     # res.update(
    #     #     credit_account_id=ICPSudo.get_param('account.credit_account_id')
    #     # )
    #     return res

class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    @api.model
    def create_exchange_rate_entry(self, aml_to_fix, amount_diff, diff_in_currency, currency, move):
        """
        Automatically create a journal items to book the exchange rate
        differences that can occure in multi-currencies environment. That
        new journal item will be made into the given `move` in the company
        `currency_exchange_journal_id`, and one of its journal items is
        matched with the other lines to balance the full reconciliation.

        :param aml_to_fix: recordset of account.move.line (possible several
            but sharing the same currency)
        :param amount_diff: float. Amount in company currency to fix
        :param diff_in_currency: float. Amount in foreign currency `currency`
            to fix
        :param currency: res.currency
        :param move: account.move
        :return: tuple.
            [0]: account.move.line created to balance the `aml_to_fix`
            [1]: recordset of account.partial.reconcile created between the
                tuple first element and the `aml_to_fix`
        """
        partial_rec = self.env['account.partial.reconcile']
        aml_model = self.env['account.move.line']

        amount_diff = move.company_id.currency_id.round(amount_diff)
        diff_in_currency = currency and currency.round(diff_in_currency) or 0

        created_lines = self.env['account.move.line']
        for aml in aml_to_fix:
            
            ICPSudo = self.env['ir.config_parameter'].sudo()
            # exchange_account_type = ICPSudo.get_param('account.exchange_account_type')
            exchange_account_type = move.company_id.exchange_account_type
            exchange_journal = move.company_id.currency_exchange_journal_id
            if exchange_account_type == 'account':
                account_id = amount_diff > 0 and move.company_id.debit_account_id.id or move.company_id.credit_account_id.id
            else:
                account_id = amount_diff > 0 and exchange_journal.default_debit_account_id.id or exchange_journal.default_credit_account_id.id
            aml.amount_residual = amount_diff
            #create the line that will compensate all the aml_to_fix
            line_to_rec = aml_model.with_context(check_move_validity=False).create({
                'name': _('Currency exchange rate difference'),
                'debit': amount_diff < 0 and -aml.amount_residual or 0.0,
                'credit': amount_diff > 0 and aml.amount_residual or 0.0,
                'account_id': aml.account_id.id,
                'move_id': move.id,
                'currency_id': currency.id,
                'amount_currency': diff_in_currency and -aml.amount_residual_currency or 0.0,
                'partner_id': aml.partner_id.id,
                'exchange_flag': True,
            })
            #create the counterpart on exchange gain/loss account
            
            aml_model.with_context(check_move_validity=False).create({
                'name': _('Currency exchange rate difference'),
                'debit': amount_diff > 0 and aml.amount_residual or 0.0,
                'credit': amount_diff < 0 and -aml.amount_residual or 0.0,
                # 'account_id': amount_diff > 0 and exchange_journal.default_debit_account_id.id or exchange_journal.default_credit_account_id.id,
                'account_id': account_id,
                'move_id': move.id,
                'currency_id': currency.id,
                'amount_currency': diff_in_currency and aml.amount_residual_currency or 0.0,
                'partner_id': aml.partner_id.id,
                'exchange_flag': True,
            })

            #reconcile all aml_to_fix
            partial_payment = self.company_id.partial_payment
            if partial_payment != True:
                partial_rec |= self.with_context(skip_full_reconcile_check=True).create(
                    self._prepare_exchange_diff_partial_reconcile(
                            aml=aml,
                            line_to_reconcile=line_to_rec,
                            currency=currency)
                )
            created_lines |= line_to_rec
        return created_lines, partial_rec

    def _compute_partial_lines(self):
        
        if self._context.get('skip_full_reconcile_check'):
            #when running the manual reconciliation wizard, don't check the partials separately for full
            #reconciliation or exchange rate because it is handled manually after the whole processing
            return self
        #check if the reconcilation is full
        #first, gather all journal items involved in the reconciliation just created
        aml_set = aml_to_balance = self.env['account.move.line']
        total_debit = 0
        total_credit = 0
        total_amount_currency = 0
        #make sure that all partial reconciliations share the same secondary currency otherwise it's not
        #possible to compute the exchange difference entry and it has to be done manually.
        currency = self[0].currency_id
        maxdate = '0000-00-00'
        sample_move_id = False
        seen = set()
        todo = set(self)
        while todo:
            partial_rec = todo.pop()
            seen.add(partial_rec)
            if partial_rec.currency_id != currency:
                #no exchange rate entry will be created
                currency = None
                # stop
            for aml in [partial_rec.debit_move_id, partial_rec.credit_move_id]:
                sample_move_id = partial_rec.credit_move_id.move_id
                
                if aml_set:
                    ss_date = aml_set[0].date

                if aml not in aml_set:
                    if aml.amount_residual or aml.amount_residual_currency:
                        aml_to_balance |= aml
                    maxdate = max(aml.date, maxdate)
                    total_debit += aml.debit
                    total_credit += aml.credit
                    aml_set |= aml
                    if aml.currency_id and aml.currency_id == currency:
                        # total_amount_currency += aml.amount_currency
                        total_amount_currency += aml.amount_currency
                        if aml_set:
                            # if aml.amount_currency > 0:
                            amt_tot = aml_set[0].amount_currency- total_amount_currency
                            # amt_tot = aml_set[0].amount_currency + aml.amount_currency
                            rate_ids = self.env['res.currency.rate'].search([('name','=',aml_set[0].date),('currency_id','=',aml_set[0].currency_id.id)])
                            if partial_rec.debit_move_id.invoice_id.currency_rate:
                                final_rate = amt_tot * partial_rec.debit_move_id.invoice_id.currency_rate
                                total_debit = final_rate
                            else:
                                if rate_ids:
                                    final_rate = amt_tot * (1/rate_ids[-1].rate)
                                    total_debit = final_rate
                            # else:
                            #     amt_tot = aml_set[0].amount_currency+aml.amount_currency
                            #     # amt_tot = aml_set[0].amount_currency + aml.amount_currency
                            #     rate_ids = self.env['res.currency.rate'].search([('name','=',aml_set[0].date),('currency_id','=',aml_set[0].currency_id.id)])
                            #     if rate_ids:
                            #         ('(1/rate_ids.rate)',(1/rate_ids.rate))
                            #         final_rate = amt_tot * (1/rate_ids.rate)
                            #         total_credit = final_rate
                    elif partial_rec.currency_id and partial_rec.currency_id == currency:
                        #if the aml has no secondary currency but is reconciled with other journal item(s) in secondary currency, the amount
                        #currency is recorded on the partial rec and in order to check if the reconciliation is total, we need to convert the
                        #aml.balance in that foreign currency
                        total_amount_currency += aml.company_id.currency_id.with_context(date=aml.date).compute(aml.balance, partial_rec.currency_id)
                if not self.company_id.partial_payment:
                    for x in aml.matched_debit_ids | aml.matched_credit_ids:
                        if x not in seen:
                            todo.add(x)

        partial_rec_ids = [x.id for x in seen]
        aml_ids = aml_set.ids
        #then, if the total debit and credit are equal, or the total amount in currency is 0, the reconciliation is full
        digits_rounding_precision = aml_set[0].company_id.currency_id.rounding
        
        if (currency and float_is_zero(total_amount_currency, precision_rounding=currency.rounding)) or float_compare(total_debit, total_credit, precision_rounding=digits_rounding_precision) == 0:
            exchange_move_id = False
            if currency and aml_to_balance:

                ICPSudo = self.env['ir.config_parameter'].sudo()
                # exchange_account_type = ICPSudo.get_param('account.exchange_account_type')
                exchange_account_type = self.company_id.exchange_account_type
                if exchange_account_type == 'account':
#                     stop
                    #eventually create a journal entry to book the difference due to foreign currency's exchange rate that fluctuates
                    rate_diff_amls, rate_diff_partial_rec = self.create_exchange_rate_entry(aml_to_balance, total_debit - total_credit, total_amount_currency, currency, sample_move_id)
                    aml_ids += rate_diff_amls.ids
                    partial_rec_ids += rate_diff_partial_rec.ids
                    sample_move_id.post()
                    exchange_move_id = sample_move_id.id
                else:
                    exchange_move = self.env['account.move'].create(
                        self.env['account.full.reconcile']._prepare_exchange_diff_move(move_date=maxdate, company=aml_to_balance[0].company_id))
                    # stop
                    #eventually create a journal entry to book the difference due to foreign currency's exchange rate that fluctuates
                    
                    rate_diff_amls, rate_diff_partial_rec = self.create_exchange_rate_entry(aml_to_balance, total_debit - total_credit, total_amount_currency, currency, exchange_move)
                    aml_ids += rate_diff_amls.ids
                    partial_rec_ids += rate_diff_partial_rec.ids
                    exchange_move.post()
                    exchange_move_id = exchange_move.id
                
            #mark the reference of the full reconciliation on the partial ones and on the entries
            self.env['account.full.reconcile'].create({
                'partial_reconcile_ids': [(6, 0, partial_rec_ids)],
                'reconciled_line_ids': [(6, 0, aml_ids)],
                'exchange_move_id': exchange_move_id,
            })
        else:
            partial_payment = self.company_id.partial_payment
            if partial_payment and partial_payment == True:
                exchange_move_id = False
                if currency and aml_to_balance:

                    ICPSudo = self.env['ir.config_parameter'].sudo()
                    # exchange_account_type = ICPSudo.get_param('account.exchange_account_type')
                    exchange_account_type = self.company_id.exchange_account_type
                    if exchange_account_type == 'account':
                        #eventually create a journal entry to book the difference due to foreign currency's exchange rate that fluctuates
                        total_amount_currency = 0
                        rate_diff_amls, rate_diff_partial_rec = self.create_exchange_rate_entry(aml_to_balance[0], total_debit - total_credit, total_amount_currency, currency, sample_move_id)
                        # aml_ids += rate_diff_amls.ids
                        # partial_rec_ids += rate_diff_partial_rec.ids
                        sample_move_id.post()
                        # exchange_move_id = sample_move_id.id
                    else:
                        exchange_move = self.env['account.move'].create(
                            self.env['account.full.reconcile']._prepare_exchange_diff_move(move_date=maxdate, company=aml_to_balance[0].company_id))
                        #eventually create a journal entry to book the difference due to foreign currency's exchange rate that fluctuates


                        # de_cr_amt = (total_credit / (1 / currency.rate))
                        # de_cr_amt = 1100
                        # total_amount_currency = 0
                        # stop
                        total_amount_currency = 0
                        
                        rate_diff_amls, rate_diff_partial_rec = self.create_exchange_rate_entry(aml_to_balance[0], total_debit - total_credit, total_amount_currency, currency, exchange_move)
                        # aml_ids += rate_diff_amls.ids
                        # partial_rec_ids += rate_diff_partial_rec.ids
                        exchange_move.post()
                        exchange_move_id = exchange_move.id
        # stop