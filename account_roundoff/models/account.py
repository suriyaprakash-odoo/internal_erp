# -*- coding: utf-8 -*-

from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import fields, models, api, _


class RoundOffSetting(models.TransientModel):
    _inherit = 'res.config.settings'
    
    round_off = fields.Boolean(string='Allow rounding of invoice amount', help="Allow rounding of invoice amount")
    round_off_account = fields.Many2one('account.account', string='Round Off Account')

    # @api.multi
    # def set_round_off(self):
    #     ir_values_obj = self.env['ir.values']
    #     ir_values_obj.sudo().set_default('res.config.settings', "round_off", self.round_off)
        # ir_values_obj.sudo().set_default('account.config.settings', "round_off_account", self.round_off_account.id)

    def set_values(self):
        super(RoundOffSetting, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('account.round_off', self.round_off)

    #To get values from respected model #
    @api.model
    def get_values(self):
        res = super(RoundOffSetting, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            round_off=ICPSudo.get_param('account.round_off'),
        )
        return res

class AccountRoundOff(models.Model):
    _inherit = 'account.invoice'

    round_off_value = fields.Monetary(compute='_compute_amount', string='Round off amount')
    rounded_total = fields.Float(compute='_compute_amount', string='Rounded Total')
    round_active = fields.Boolean(compute='get_round_active')

    def get_round_active(self):
        # ir_values = self.env['ir.values']
        for i in self:
            ICPSudo = self.env['ir.config_parameter'].sudo()
            round_active = ICPSudo.get_param('account.round_off')
            # i.round_active = ir_values.get_default('res.config.settings', 'round_off')
            i.round_active = round_active

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id',
                 'date_invoice', 'type')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        ICPSudo = self.env['ir.config_parameter'].sudo()
        round_active = ICPSudo.get_param('account.round_off')
        
        if self.round_active == True or round_active == 'True':
            self.rounded_total = round(self.amount_untaxed + self.amount_tax)
        else:
            self.rounded_total = self.amount_untaxed + self.amount_tax

        self.amount_total = self.amount_untaxed + self.amount_tax
        self.round_off_value = self.rounded_total - (self.amount_untaxed + self.amount_tax)
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
        self.amount_total= self.rounded_total
        self.amount_total_signed = self.rounded_total
        
        # for line in self.invoice_line_ids:
        #     line.price_subtotal = round(line.price_subtotal,0)

    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        
        for line in self.sudo().move_id.line_ids:
            if line.account_id.internal_type in ('receivable', 'payable'):
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(
                        date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                    residual += from_currency.compute(line.amount_residual, self.currency_id)

        if self.round_active is True:
            self.residual_company_signed = round(abs(residual_company_signed)) * sign
            self.residual_signed = round(abs(residual)) * sign
            self.residual = round(abs(residual))
        else:
            self.residual_company_signed = abs(residual_company_signed) * sign
            self.residual_signed = abs(residual) * sign
            self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

    # @api.multi
    # def action_move_create(self):
    #     """ Creates invoice related analytics and financial move lines """
    #     account_move = self.env['account.move']

    #     for inv in self:

    #         if not inv.journal_id.sequence_id:
    #             raise UserError(_('Please define sequence on the journal related to this invoice.'))
    #         if not inv.invoice_line_ids:
    #             raise UserError(_('Please create some invoice lines.'))
    #         if inv.move_id:
    #             continue

    #         ctx = dict(self._context, lang=inv.partner_id.lang)

    #         if not inv.date_invoice:
    #             inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
    #         date_invoice = inv.date_invoice
    #         company_currency = inv.company_id.currency_id

    #         # create move lines (one per invoice line + eventual taxes and analytic lines)
    #         iml = inv.invoice_line_move_line_get()
    #         iml += inv.tax_line_move_line_get()

    #         diff_currency = inv.currency_id != company_currency
    #         # create one move line for the total and possibly adjust the other lines amount
    #         total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

    #         name = inv.name or '/'
    #         if inv.payment_term_id:
    #             totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(
    #                 total, date_invoice)[0]
    #             res_amount_currency = total_currency
    #             ctx['date'] = date_invoice
    #             for i, t in enumerate(totlines):
    #                 if inv.currency_id != company_currency:
    #                     amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
    #                 else:
    #                     amount_currency = False

    #                 # last line: add the diff
    #                 res_amount_currency -= amount_currency or 0
    #                 if i + 1 == len(totlines):
    #                     amount_currency += res_amount_currency
    #                 if self.round_active is True:
    #                     if self.round_off_value > 0:
    #                         amount = t[1] - (inv.type in ('in_invoice', 'out_refund') and abs(self.round_off_value) or self.round_off_value)
    #                         if inv.type in ('out_invoice', 'in_refund'):
    #                             amount = t[1] - (inv.type in ('in_invoice', 'out_refund') and abs(self.round_off_value) or -self.round_off_value)
    #                     else:
    #                         amount = t[1] + (inv.type in ('in_invoice', 'out_refund') and abs(self.round_off_value) or self.round_off_value)
    #                     iml.append({
    #                         'type': 'dest',
    #                         'name': name,
    #                         'price': amount,
    #                         'account_id': inv.account_id.id,
    #                         'date_maturity': t[0],
    #                         'amount_currency': diff_currency and amount_currency,
    #                         'currency_id': diff_currency and inv.currency_id.id,
    #                         'invoice_id': inv.id
    #                     })
    #                     ir_values = self.env['ir.values']
    #                     # acc_id = ir_values.get_default('account.config.settings', 'round_off_account')
    #                     acc_id = ir_values.get_default('account.config.settings')
    #                     if self.round_off_value != 0:
    #                         iml.append({
    #                             'type': 'dest',
    #                             'name': "Round off",
    #                             'price': (inv.type in ('in_invoice', 'out_refund') and self.round_off_value or -self.round_off_value),
    #                             'account_id': acc_id,
    #                             'date_maturity': inv.date_due,
    #                             'amount_currency': diff_currency and total_currency,
    #                             'currency_id': diff_currency and inv.currency_id.id,
    #                             'invoice_id': inv.id
    #                         })
                            
    #                 else:
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

    #         else:
    #             if self.round_active is True:
    #                 if self.round_off_value > 0:
    #                     amount = -(inv.type in ('in_invoice', 'out_refund') and abs(self.round_off_value) or self.round_off_value)
    #                     if inv.type in ('out_invoice', 'in_refund'):
    #                         amount = -(inv.type in ('in_invoice', 'out_refund') and abs(self.round_off_value) or -self.round_off_value)
    #                 else:
    #                     amount = (inv.type in ('in_invoice', 'out_refund') and abs(self.round_off_value) or self.round_off_value)
    #                 iml.append({
    #                     'type': 'dest',
    #                     'name': name,
    #                     'price': total + amount,
    #                     'account_id': inv.account_id.id,
    #                     'date_maturity': inv.date_due,
    #                     'amount_currency': diff_currency and total_currency,
    #                     'currency_id': diff_currency and inv.currency_id.id,
    #                     'invoice_id': inv.id
    #                 })
    #                 ir_values = self.env['ir.values']
    #                 # acc_id = ir_values.get_default('account.config.settings', 'round_off_account')
    #                 acc_id = ir_values.get_default('account.config.settings')
    #                 if self.round_off_value != 0:
    #                     iml.append({
    #                         'type': 'dest',
    #                         'name': "Round off",
    #                         'price': (inv.type in ('in_invoice', 'out_refund') and self.round_off_value or -self.round_off_value),
    #                         'account_id': acc_id,
    #                         'date_maturity': inv.date_due,
    #                         'amount_currency': diff_currency and total_currency,
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
    #         part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
    #         line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
    #         line = inv.group_lines(iml, line)
    #         journal = inv.journal_id.with_context(ctx)
    #         line = inv.finalize_invoice_move_lines(line)

    #         date = inv.date or date_invoice
    #         move_vals = {
    #             'ref': inv.reference,
    #             'line_ids': line,
    #             'journal_id': journal.id,
    #             'date': date,
    #             'narration': inv.comment,
    #         }
    #         ctx['company_id'] = inv.company_id.id
    #         ctx['invoice'] = inv
    #         ctx_nolang = ctx.copy()
    #         ctx_nolang.pop('lang', None)
    #         move = account_move.with_context(ctx_nolang).create(move_vals)
    #         # Pass invoice in context in method post: used if you want to get the same
    #         # account move reference when creating the same invoice after a cancelled one:
    #         move.post()
    #         # make the invoice point to that move
    #         vals = {
    #             'move_id': move.id,
    #             'date': date,
    #             'move_name': move.name,
    #         }
    #         inv.with_context(ctx).write(vals)
    #     return True

# class AccountInvoiceLine(models.Model):
#     _inherit = 'account.invoice.line'

#     @api.one
#     @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
#         'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
#         'invoice_id.date_invoice', 'invoice_id.date')
#     def _compute_price(self):
#         currency = self.invoice_id and self.invoice_id.currency_id or None
#         price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
#         taxes = False
#         if self.invoice_line_tax_ids:
#             taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
#         if self.invoice_id.round_active == True:
#             self.price_subtotal = price_subtotal_signed = round(taxes['total_excluded'] if taxes else self.quantity * price,0)
#             self.price_total = round(taxes['total_included'] if taxes else self.price_subtotal,0)
#         else:
#             self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
#             self.price_total = taxes['total_included'] if taxes else self.price_subtotal
#         if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
#             price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id._get_currency_rate_date()).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
#         sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
#         self.price_subtotal_signed = price_subtotal_signed * sign