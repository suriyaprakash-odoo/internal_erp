from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = "account.move"

    check_number = fields.Char('Check Number')
                     
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    tds_payment_id = fields.Many2one('tds.payment')
    
#     @api.multi
#     def remove_move_reconcile(self):
#         move_line_ids = self.search([('move_id','=',self.move_id.id),('exchange_flag','=',True)])
#         list_ids = ",".join(map(str,move_line_ids.ids))
#         if move_line_ids:
#             self._cr.execute(''' delete from account_move_line WHERE id in (%s) '''%(list_ids))
# 
#         """ Undo a reconciliation """
#         if not self:
#             return True
#         rec_move_ids = self.env['account.partial.reconcile']
#         for account_move_line in self:
#             for invoice in account_move_line.payment_id.invoice_ids:
#                 if account_move_line in invoice.payment_move_line_ids:
#                     account_move_line.payment_id.write({'invoice_ids': [(3, invoice.id, None)]})
#             # 2017 George
#             partial_move_ids = self.env['account.partial.reconcile'].search([('credit_move_id', '=', account_move_line.id)])
#             if len(partial_move_ids) <=1:
#                 for partial_move_id in partial_move_ids:
#                     partial_move_id.write({'da_shown':'no'})
#                     da_line_id = self.env['account.invoice.amount.line'].search([('move_line_id', '=', partial_move_id.credit_move_id.id)])
#                     da_line_id.unlink()
#             partial_move_ids = self.env['account.partial.reconcile'].search([('debit_move_id', '=', account_move_line.id)])
#             if len(partial_move_ids)<= 1 :
#                 for partial_move_id in partial_move_ids :
#                     partial_move_id.write({'da_shown' : 'no'})
#                     da_line_id = self.env['account.invoice.amount.line'].search([('move_line_id', '=', partial_move_id.debit_move_id.id)])
#                     da_line_id.unlink()
# 
# 
#             rec_move_ids += account_move_line.matched_debit_ids
#             rec_move_ids += account_move_line.matched_credit_ids
#         return rec_move_ids.unlink()
                                
    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False, invoice_type=False, invoice=None):
        company_ids = set()
        all_accounts = []
        partners = set()
        for line in self:
            company_ids.add(line.company_id.id)
            all_accounts.append(line.account_id)
            if (line.account_id.internal_type in ('receivable', 'payable')):
                partners.add(line.partner_id.id)
            if line.reconciled:
                raise UserError(_('You are trying to reconcile some entries that are already reconciled!'))
        if len(company_ids) > 1:
            raise UserError(_('To reconcile the entries company should be the same for all entries!'))
        if len(set(all_accounts)) > 1:
            raise UserError(_('Entries are not of the same account!'))
        if not all_accounts[0].reconcile:
            raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (all_accounts[0].name, all_accounts[0].code))
        if len(partners) > 1:
            raise UserError(_('The partner has to be the same on all lines for receivable and payable accounts!'))
        
        self_ids = self.env['account.move.line']
        self_ids = self
        remaining_moves = self.auto_reconcile_lines( invoice_type=invoice_type, invoice=invoice)
        if writeoff_acc_id and writeoff_journal_id and remaining_moves:
            self_ids = self_ids - remaining_moves
            all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
            writeoff_vals = {
                'account_id': writeoff_acc_id.id,
                'journal_id': writeoff_journal_id.id
            }
            if not all_aml_share_same_currency:
                writeoff_vals['amount_currency'] = False
            writeoff_vals['move_line_id'] = self_ids   
            writeoff_to_reconcile = remaining_moves._create_writeoff(writeoff_vals)
            remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines( invoice_type=invoice_type, invoice=invoice)
            return writeoff_to_reconcile
        return True
    
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
            'da_type':invoice_type,
        })
        return self.auto_reconcile_lines()
