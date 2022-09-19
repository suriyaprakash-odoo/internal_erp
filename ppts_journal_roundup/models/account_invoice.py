# -*- coding: utf-8 -*-

# from odoo.tools.float_utils import float_round as round
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
#     @api.model
#     def line_get_convert(self, line, part):
#         
#         credit = line['price'] < 0 and -line['price']
#         debit = line['price'] > 0 and line['price']
#         
#         return {
#             'date_maturity': line.get('date_maturity', False),
#             'partner_id': part,
#             'name': line['name'],
#             'debit': round(debit) if self.journal_id.round_up else line['price'] > 0 and line['price'],
#             'credit': round(credit) if self.journal_id.round_up else line['price'] < 0 and -line['price'],
#             'account_id': line['account_id'],
#             'analytic_line_ids': line.get('analytic_line_ids', []),
#             'amount_currency': line['price'] > 0 and abs(line.get('amount_currency', False)) or -abs(line.get('amount_currency', False)),
#             'currency_id': line.get('currency_id', False),
#             'quantity': line.get('quantity', 1.00),
#             'product_id': line.get('product_id', False),
#             'product_uom_id': line.get('uom_id', False),
#             'analytic_account_id': line.get('account_analytic_id', False),
#             'invoice_id': line.get('invoice_id', False),
#             'tax_ids': line.get('tax_ids', False),
#             'tax_line_id': line.get('tax_line_id', False),
#             'analytic_tag_ids': line.get('analytic_tag_ids', False),
#         }
        
#     @api.multi
#     def action_move_create(self):
#         """ Creates invoice related analytics and financial move lines """
#         account_move = self.env['account.move']
# 
#         for inv in self:
#             if not inv.journal_id.sequence_id:
#                 raise UserError(_('Please define sequence on the journal related to this invoice.'))
#             if not inv.invoice_line_ids:
#                 raise UserError(_('Please create some invoice lines.'))
#             if inv.move_id:
#                 continue
# 
#             ctx = dict(self._context, lang=inv.partner_id.lang)
# 
#             if not inv.date_invoice:
#                 inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
#             if not inv.date_due:
#                 inv.with_context(ctx).write({'date_due': inv.date_invoice})
#             company_currency = inv.company_id.currency_id
# 
#             # create move lines (one per invoice line + eventual taxes and analytic lines)
#             iml = inv.invoice_line_move_line_get()
#             iml += inv.tax_line_move_line_get()
# 
#             diff_currency = inv.currency_id != company_currency
#             # create one move line for the total and possibly adjust the other lines amount
#             total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)
# 
#             name = inv.name or '/'
#             if inv.payment_term_id:
#                 totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
#                 res_amount_currency = total_currency
#                 ctx['date'] = inv._get_currency_rate_date()
#                 for i, t in enumerate(totlines):
#                     if inv.currency_id != company_currency:
#                         amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
#                     else:
#                         amount_currency = False
# 
#                     # last line: add the diff
#                     res_amount_currency -= amount_currency or 0
#                     if i + 1 == len(totlines):
#                         amount_currency += res_amount_currency
# 
#                     iml.append({
#                         'type': 'dest',
#                         'name': name,
#                         'price': t[1],
#                         'account_id': inv.account_id.id,
#                         'date_maturity': t[0],
#                         'amount_currency': diff_currency and amount_currency,
#                         'currency_id': diff_currency and inv.currency_id.id,
#                         'invoice_id': inv.id
#                     })
#             else:
#                 iml.append({
#                     'type': 'dest',
#                     'name': name,
#                     'price': total,
#                     'account_id': inv.account_id.id,
#                     'date_maturity': inv.date_due,
#                     'amount_currency': diff_currency and total_currency,
#                     'currency_id': diff_currency and inv.currency_id.id,
#                     'invoice_id': inv.id
#                 })
#             part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
#             line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
#             line = inv.group_lines(iml, line)
# 
#             journal = inv.journal_id.with_context(ctx)
#             line = inv.finalize_invoice_move_lines(line)
# 
#             date = inv.date or inv.date_invoice
#             move_vals = {
#                 'ref': inv.reference,
#                 'line_ids': line,
#                 'journal_id': journal.id,
#                 'date': date,
#                 'narration': inv.comment,
#             }
#             ctx['company_id'] = inv.company_id.id
#             ctx['invoice'] = inv
#             ctx_nolang = ctx.copy()
#             ctx_nolang.pop('lang', None)
#             move = account_move.with_context(ctx_nolang).create(move_vals)
#             if self.journal_id.round_up:
#                 self.set_balance_amount(move)
#             # Pass invoice in context in method post: used if you want to get the same
#             # account move reference when creating the same invoice after a cancelled one:
#             move.post()
#             # make the invoice point to that move
#             vals = {
#                 'move_id': move.id,
#                 'date': date,
#                 'move_name': move.name,
#             }
#             inv.with_context(ctx).write(vals)
#         return True
    
    def set_balance_amount(self,move):
        for line in move.line_ids:
            line.credit = round(line.credit)
            line.debit = round(line.debit)
        total_cr = sum([line.credit for line in move.line_ids])
        total_dr = sum([line.debit for line in move.line_ids])
        total_diff_cr = 0
        total_diff_dr = 0
        
        if total_cr > total_dr:
            total_diff_dr = total_cr-total_dr
        elif total_cr < total_dr:
            total_diff_cr = total_dr-total_cr
            
        if (total_diff_cr > 0) or (total_diff_dr > 0):
            
            vals= {
            'date_maturity': move.date,
            'partner_id': self.partner_id.id,
            'name': self.company_id.roundoff_label if self.company_id.roundoff_label else "/",
            'debit': total_diff_dr,
            'credit': total_diff_cr,
            'account_id': self.company_id.roundup_account_id.id,
            'analytic_line_ids': [],
            'amount_currency': 0,
            'currency_id': self.currency_id.id,
            'quantity': 1.00,
            'product_id': False,    
            'product_uom_id': False,
            'analytic_account_id': False,
            'invoice_id': self.id,
            'move_id': move.id,
#             'tax_ids': line.get('tax_ids', False),
#             'tax_line_id': line.get('tax_line_id', False),
#             'analytic_tag_ids': line.get('analytic_tag_ids', False),
            }
            move_line_id = self.env['account.move.line'].create(vals)
        
            
            
            
            
        
        
    
    