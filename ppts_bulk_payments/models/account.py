from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

# from openerp import api, fields, models, _
# from openerp.exceptions import RedirectWarning, UserError

class AccountAccountType(models.Model):
    _inherit = "account.account.type"
    _description = "Account Type"

    is_visible = fields.Boolean(string="Hide")

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    # @api.v7
    # def assign_outstanding_credit(self, cr, uid, id, credit_aml_id, context=None):
    #     credit_aml = self.pool.get('account.move.line').browse(cr, uid, credit_aml_id, context=context)
    #     inv = self.browse(cr, uid, id, context=context)
    #     if not credit_aml.currency_id and inv.currency_id != inv.company_id.currency_id:
    #         credit_aml.with_context(allow_amount_currency=True).write({
    #             'amount_currency': inv.company_id.currency_id.with_context(date=credit_aml.date).compute(credit_aml.balance, inv.currency_id),
    #             'currency_id': inv.currency_id.id})
    #     if credit_aml.payment_id:
    #         credit_aml.payment_id.write({'invoice_ids': [(4, id, None)]})
    #     return inv.register_payment(credit_aml, writeoff_acc_id=False, writeoff_journal_id=False, invoice_type= inv.type)


#     @api.multi
#     def register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False, invoice_type=False):
#         """ Reconcile payable/receivable lines from the invoice with payment_line """
#         line_to_reconcile = self.env['account.move.line']
#         for inv in self:
#             line_to_reconcile += inv.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
#         return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id, invoice_type=invoice_type)

    def update_invoice_ref(self, cr, uid, ids, context=None):
        cr.execute("update account_move_line set draft_assigned_to_statement = 'f' where move_id in (4755, 5944) and account_id = 4;")
        return True

class AccountAccount(models.Model):
    _inherit = "account.account"

    user_type_id = fields.Many2one('account.account.type', string='Account Type', required=True, oldname="user_type", 
        help="Account Type is used for information purpose, to generate country-specific legal reports, and set the rules to close a fiscal year and generate opening entries.")



# class ReportTrialBalance(models.AbstractModel):
#     _inherit = 'report.account.report_trialbalance'

#     def _get_accounts(self, accounts, display_account):
#         """ compute the balance, debit and credit for the provided accounts
#             :Arguments:
#                 `accounts`: list of accounts record,
#                 `display_account`: it's used to display either all accounts or those accounts which balance is > 0
#             :Returns a list of dictionary of Accounts with following key and value
#                 `name`: Account name,
#                 `code`: Account code,
#                 `credit`: total amount of credit,
#                 `debit`: total amount of debit,
#                 `balance`: total amount of balance,
#         """

#         account_result = {}
#         # Prepare sql query base on selected parameters from wizard
#         tables, where_clause, where_params = self.env['account.move.line']._query_get()
#         tables = tables.replace('"','')
#         if not tables:
#             tables = 'account_move_line'
#         wheres = [""]
#         if where_clause.strip():
#             wheres.append(where_clause.strip())
#         filters = " AND ".join(wheres)
#         # compute the balance, debit and credit for the provided accounts
#         request = ("SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" +\
#                    " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
#         params = (tuple(accounts.ids),) + tuple(where_params)
#         self.env.cr.execute(request, params)
#         for row in self.env.cr.dictfetchall():
#             account_result[row.pop('id')] = row

#         account_res = []
#         for account in accounts:
#             if account.user_type_id:
#                 account_type_obj=self.env['account.account.type'].search([('id', '=', account.user_type_id.id)])
#                 if not account_type_obj.is_visible:
#                     res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
#                     currency = account.currency_id and account.currency_id or account.company_id.currency_id
#                     res['code'] = account.code
#                     res['name'] = account.name
#                     if account.id in account_result.keys():
#                         res['debit'] = account_result[account.id].get('debit')
#                         res['credit'] = account_result[account.id].get('credit')
#                         res['balance'] = account_result[account.id].get('balance')
#                     if display_account == 'all':
#                         account_res.append(res)
#                     if display_account in ['movement', 'not_zero'] and not currency.is_zero(res['balance']):
#                         account_res.append(res)
#         return account_res



# class ReportFinancial(models.AbstractModel):
#     _inherit = 'report.account.report_financial'

#     def get_account_lines(self, data):
#         lines = []
#         account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
#         child_reports = account_report._get_children_by_order()
#         res = self.with_context(data.get('used_context'))._compute_report_balance(child_reports)
#         if data['enable_filter']:
#             comparison_res = self.with_context(data.get('comparison_context'))._compute_report_balance(child_reports)
#             for report_id, value in comparison_res.items():
#                 res[report_id]['comp_bal'] = value['balance']
#                 report_acc = res[report_id].get('account')
#                 if report_acc:
#                     for account_id, val in comparison_res[report_id].get('account').items():
#                         report_acc[account_id]['comp_bal'] = val['balance']

#         for report in child_reports:
#             h_vals = {
#                 'name': report.name,
#                 'balance': res[report.id]['balance'] * report.sign,
#                 'type': 'report',
#                 'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
#                 'account_type': report.type or False, #used to underline the financial report balances
#             }
#             if data['debit_credit']:
#                 h_vals['debit'] = res[report.id]['debit']
#                 h_vals['credit'] = res[report.id]['credit']

#             if data['enable_filter']:
#                 h_vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign
            
#             if report.name == 'Profit and Loss':
#                 h_vals.update({
#                                   'balance': res[report.id]['balance'] * report.sign,
#                         })
#             else:
#                 if report.display_detail != 'no_detail':
#                 #the rest of the loop is used to display the details of the financial report, so it's not needed here.
#                     balance=0.0
#                     if res[report.id].get('account'):
#                         sub_lines = []
#                         for account_id, value in res[report.id]['account'].items():
#                             #if there are accounts to display, we add them to the lines with a level equals to their level in
#                             #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
#                             #financial reports for Assets, liabilities...)
#                             flag = False
#                             account = self.env['account.account'].browse(account_id)
#                             if account.user_type_id:
#                                 account_type_obj=self.env['account.account.type'].search([('id', '=', account.user_type_id.id)])
#                                 if not account_type_obj.is_visible:
#                                     balance = value['balance'] * report.sign +balance
                                
#                     h_vals.update({
#                                   'balance': balance * report.sign,
#                         })
                
#             lines.append(h_vals)
                            
#             if report.display_detail == 'no_detail':
#                 #the rest of the loop is used to display the details of the financial report, so it's not needed here.
#                 continue
#             balance=0.0
#             if res[report.id].get('account'):
#                 sub_lines = []
#                 for account_id, value in res[report.id]['account'].items():
#                     #if there are accounts to display, we add them to the lines with a level equals to their level in
#                     #the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
#                     #financial reports for Assets, liabilities...)
#                     flag = False
#                     account = self.env['account.account'].browse(account_id)
#                     if account.user_type_id:
#                         account_type_obj=self.env['account.account.type'].search([('id', '=', account.user_type_id.id)])
#                         if not account_type_obj.is_visible:
#                             vals = {
#                                 'name': account.code + ' ' + account.name,
#                                 'balance': value['balance'] * report.sign or 0.0,
#                                 'type': 'account',
#                                 'level': report.display_detail == 'detail_with_hierarchy' and 4,
#                                 'account_type': account.internal_type,
#                             }
#                             if data['debit_credit']:
#                                 vals['debit'] = value['debit']
#                                 vals['credit'] = value['credit']
#                                 if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
#                                     flag = True
#                             if not account.company_id.currency_id.is_zero(vals['balance']):
#                                 flag = True
#                             if data['enable_filter']:
#                                 vals['balance_cmp'] = value['comp_bal'] * report.sign
#                                 if not account.company_id.currency_id.is_zero(vals['balance_cmp']):
#                                     flag = True
#                             if flag:
#                                 sub_lines.append(vals)
                            
#                 lines += sorted(sub_lines, key=lambda sub_line: sub_line['name'])
            
#         return lines
    
    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    exchange_flag = fields.Boolean('Exchange Flag')
    statement_status = fields.Boolean(string = 'BRS Status', readonly = True, track_visibility = 'onchange')
    seq_no = fields.Char(string = 'Bank Acc Rec Sequence')
    
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
# # 2017 George
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
# 
#     @api.multi
#     def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False, invoice_type=False):
#         #Perform all checks on lines
#         company_ids = set()
#         all_accounts = []
#         partners = set()
#         for line in self:
#             company_ids.add(line.company_id.id)
#             all_accounts.append(line.account_id)
#             if (line.account_id.internal_type in ('receivable', 'payable')):
#                 partners.add(line.partner_id.id)
#             if line.reconciled:
#                 raise UserError(_('You are trying to reconcile some entries that are already reconciled!'))
#         if len(company_ids) > 1:
#             raise UserError(_('To reconcile the entries company should be the same for all entries!'))
#         if len(set(all_accounts)) > 1:
#             raise UserError(_('Entries are not of the same account!'))
#         if not all_accounts[0].reconcile:
#             raise UserError(_('The account %s (%s) is not marked as reconciliable !') % (all_accounts[0].name, all_accounts[0].code))
#         if len(partners) > 1:
#             raise UserError(_('The partner has to be the same on all lines for receivable and payable accounts!'))
# 
#         #reconcile everything that can be
#         remaining_moves = self.auto_reconcile_lines( invoice_type=invoice_type)
# 
#         #if writeoff_acc_id specified, then create write-off move with value the remaining amount from move in self
#         if writeoff_acc_id and writeoff_journal_id and remaining_moves:
#             all_aml_share_same_currency = all([x.currency_id == self[0].currency_id for x in self])
#             writeoff_vals = {
#                 'account_id': writeoff_acc_id.id,
#                 'journal_id': writeoff_journal_id.id
#             }
#             if not all_aml_share_same_currency:
#                 writeoff_vals['amount_currency'] = False
#             writeoff_to_reconcile = remaining_moves._create_writeoff(writeoff_vals)
#             #add writeoff line to reconcile algo and finish the reconciliation
#             remaining_moves = (remaining_moves + writeoff_to_reconcile).auto_reconcile_lines( invoice_type=invoice_type)
#             return writeoff_to_reconcile
#         return True

#     def auto_reconcile_lines(self, invoice_type=False):
#         """ This function iterates recursively on the recordset given as parameter as long as it
#             can find a debit and a credit to reconcile together. It returns the recordset of the
#             account move lines that were not reconciled during the process.
#         """
#         if not self.ids:
#             return self
#         sm_debit_move, sm_credit_move = self._get_pair_to_reconcile()
#         #there is no more pair to reconcile so return what move_line are left
#         if not sm_credit_move or not sm_debit_move:
#             return self
# 
#         field = self[0].account_id.currency_id and 'amount_residual_currency' or 'amount_residual'
#         if not sm_debit_move.debit and not sm_debit_move.credit:
#             #both debit and credit field are 0, consider the amount_residual_currency field because it's an exchange difference entry
#             field = 'amount_residual_currency'
#         if self[0].currency_id and all([x.currency_id == self[0].currency_id for x in self]):
#             #all the lines have the same currency, so we consider the amount_residual_currency field
#             field = 'amount_residual_currency'
#         if self._context.get('skip_full_reconcile_check') == 'amount_currency_excluded':
#             field = 'amount_residual'
#         elif self._context.get('skip_full_reconcile_check') == 'amount_currency_only':
#             field = 'amount_residual_currency'
#         #Reconcile the pair together
#         amount_reconcile = min(sm_debit_move[field], -sm_credit_move[field])
#         #Remove from recordset the one(s) that will be totally reconciled
#         if amount_reconcile == sm_debit_move[field]:
#             self -= sm_debit_move
#         if amount_reconcile == -sm_credit_move[field]:
#             self -= sm_credit_move
# 
#         #Check for the currency and amount_currency we can set
#         currency = False
#         amount_reconcile_currency = 0
#         if sm_debit_move.currency_id == sm_credit_move.currency_id and sm_debit_move.currency_id.id:
#             currency = sm_credit_move.currency_id.id
#             amount_reconcile_currency = min(sm_debit_move.amount_residual_currency, -sm_credit_move.amount_residual_currency)
# 
#         amount_reconcile = min(sm_debit_move.amount_residual, -sm_credit_move.amount_residual)
# 
#         if self._context.get('skip_full_reconcile_check') == 'amount_currency_excluded':
#             amount_reconcile_currency = 0.0
#             currency = self._context.get('manual_full_reconcile_currency')
#         elif self._context.get('skip_full_reconcile_check') == 'amount_currency_only':
#             currency = self._context.get('manual_full_reconcile_currency')
#         self.env['account.partial.reconcile'].create({
#             'debit_move_id': sm_debit_move.id,
#             'credit_move_id': sm_credit_move.id,
#             'amount': amount_reconcile,
#             'amount_currency': amount_reconcile_currency,
#             'currency_id': currency,
#             'da_type':invoice_type,
#         })
#         #Iterate process again on self
#         return self.auto_reconcile_lines()


    def remove_check(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'statement_status': False})
        return True    
