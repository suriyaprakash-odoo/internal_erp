# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import date
from odoo.tools import float_is_zero, float_compare, pycompat
import json

class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
    is_tds = fields.Boolean('Is TDS Applicable ?', copy=False, track_visibility='onchange')
    tds_section_id = fields.Many2one('account.tds',"TDS Section", copy=False, track_visibility='onchange')
    amount_tds = fields.Monetary('TDS Amount', store=True, compute='_compute_amount', readonly=True, copy=False, track_visibility='onchange')
    amount_tds_residual = fields.Float('Total Residual', store=True, compute='_compute_amount', readonly=True, copy=False)
    is_base_amount = fields.Boolean('Deduct TDS from Base Amount', copy=False)
    tds_reconcile_ids = fields.One2many('account.tds.reconcile', 'invoice_id', copy=False)
    reconciled_ids = fields.One2many('tds.reconciled', 'invoice_id', copy=False)
    domain_section_id = fields.Many2one('account.tds', related="partner_id.tds_section_id")
    is_tds_reconcile = fields.Boolean(default=False, copy=False)
    tds_widget = fields.Text(compute='_get_tds_info_JSON')
    tds_journal_widget = fields.Text(compute='_get_journal_tds_info_JSON')
    without_pan = fields.Boolean('Process Without PAN', track_visibility='always')
    
    @api.one
    def _get_tds_info_JSON(self):
        self.tds_widget = json.dumps(False)
        info = {'content': [], 'invoice_id': self.id}
        lines = self.env['account.tds.reconcile'].search([('invoice_id', '=', self.id)])
        if len(lines) != 0:
            for line in lines:
                info['content'].append({
                    'name': line.name,
                    'code': line.code,
                    'currency': line.currency_id.symbol,
                    'tds_amount': "{:.2f}".format(line.tds_amount),
                    'reconcile_amount': "{:.2f}".format(line.reconcile_amount),
                    'bal_amount': "{:.2f}".format(line.bal_amount),
                    'id': line.id,
                })
            self.tds_widget = json.dumps(info)

    @api.one
    def _get_journal_tds_info_JSON(self):
        self.tds_journal_widget = json.dumps(False)
        info = {'content': [], 'invoice_id': self.id}
        lines = self.env['tds.reconciled'].search([('invoice_id', '=', self.id)])
        if len(lines) != 0:
            for line in lines:
                info['content'].append({
                    'name': line.name,
                    'currency': line.currency_id.symbol,
                    'reconcile_amount': "{:.2f}".format(line.reconcile_amount),
                    'id': line.id,
                })
            self.tds_journal_widget = json.dumps(info)
        
    @api.multi
    def remove_tds_reconcile(self, paymentId):
        if paymentId:
            journal_tds_id = self.env['tds.reconciled'].browse(paymentId)
            journal_tds_id.unreconcile_tds()
            
    @api.onchange('partner_id')
    def onchange_tds_partner_id(self):
        if self.partner_id:
            self.is_tds = self.partner_id.is_tds
            self.tds_section_id = self.partner_id.tds_section_id.id
        else:
            self.is_tds = False
            self.tds_section_id = False
    
    @api.onchange('tds_section_id')
    def onchange_tds_section_id(self):
        if self.tds_section_id:
            self.is_base_amount = self.tds_section_id.deduct_base
        else:
            self.is_base_amount = False
            
    @api.multi
    def action_invoice_open(self):
        if self.is_tds:
            tds_line_ids = self.env['account.tds.line'].search([('active_line', '=', False),('date_from', '=', self.date_invoice),('tds_id', '=', self.tds_section_id.id)])
            if tds_line_ids:
                raise UserError(_("Same date"))
        if self.partner_id.tds_deductee_id.pan_check and self.partner_id.supplier:
            if not self.partner_id.pan_no:
                if self.without_pan == False:
                    raise UserError(_("No PAN is available for the selected partner.\n \
                                    If you want to continue, select Process without PAN which is in other Info tab !!! \n \
                                    Else, contact your Manager/administrator!!!"))
        res = super(AccountInvoice, self).action_invoice_open()
        for line in self.invoice_line_ids:
            tds_payment_id = self.env['account.tds.payment'].search([('invoice_line_id', '=', line.id)])
            for pay in tds_payment_id:
                pay.state = 'open'
                pay.name = self.move_id.name
        return res
    
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
                 'currency_id', 'company_id', 'date_invoice', 'type', 'invoice_line_ids.amount_tds')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        amount_tds = amount_tds_residual = 0.0
        for line in self.invoice_line_ids:
            if line.is_apply:
                for pay in line.tds_invoice_ids:
                    amount_tds += pay.bal_amount
                    amount_tds_residual += pay.tds_amount
        self.amount_tds = amount_tds
        self.amount_tds_residual = amount_tds_residual
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax - self.amount_tds
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed - self.amount_tds
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
        
    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = residual_company_signed = amount_tds = 0.0
        for line in self.invoice_line_ids:
            if line.is_apply:
                for pay in line.tds_invoice_ids:
                    amount_tds += pay.bal_amount
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id == self.account_id:
                residual_company_signed += line.amount_residual-amount_tds
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                    residual += from_currency.compute(line.amount_residual, self.currency_id)
#         residual = (abs(residual)) - amount_tds
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = (abs(residual)) * sign
        self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False
    
    @api.multi
    def clear_tds(self):
        if self.is_tds_reconcile:
            raise UserError(_("TDS Already reconciled"))
        else:
            for line in self.invoice_line_ids:
                tds_id = self.env['account.tds.payment'].search([('invoice_line_id', '=', line.id)])
                tds_id.unlink()
            for rec in self.tds_reconcile_ids:
                rec.unlink()
    
    @api.multi
    def gen_tds(self):
        if self.is_tds_reconcile:
            raise UserError(_("TDS Already reconciled"))
#         list_tds = []
#         for line in self.invoice_line_ids:
#             if line.is_apply:
#                 list_tds.append(line.invoice_id)
#         if len(list_tds)>1:
#             raise UserError(_("TDS Applicable for single line item only."))
        listids=[];residual = 0.00
        for each in self.env['account.tds.payment'].search([('partner_id', '=', self.partner_id.id),('state', '=', 'open'),('bal_amount', '>', 0.0)]):
            if each.payment_id:
                tds_invoice_ids = self.env['account.tds.reconcile'].search([('tds_payment_id','=',each.id),('bal_amount', '>', 0.0),('partner_id', '=', self.partner_id.id)])
                for tds in tds_invoice_ids:
                    if tds.invoice_id.id != self.id and tds.bal_amount!=tds.tds_amount and tds.is_reconcile and tds.bal_amount>0.0:
                        tds_invoice_id = self.env['account.tds.reconcile'].create({
                            'invoice_id': self.id,
                            'tds_payment_id': each.id,
                            'name': tds.name,
                            'date': date.today(),
                            'code': tds.code,
                            'partner_id': tds.partner_id.id,
                            'tds_section_id': tds.tds_section_id.id,
                            'account_id': tds.account_id.id,
                            'amount': tds.amount,
                            'tds_amount': tds.tds_amount,
                            'bal_amount': tds.bal_amount,
                            'reconcile_amount': tds.bal_amount,
                            'tds_payable': tds.tds_payable,
                        })
                        tds.write({
                            'tds_amount': tds.tds_amount,
                            'bal_amount': 0.0,
                            'reconcile_amount': 0.0,
                        })
                    if tds.invoice_id.id != self.id and tds.bal_amount>0.0:
                        tds_invoice_id = self.env['account.tds.reconcile'].create({
                            'invoice_id': self.id,
                            'tds_payment_id': each.id,
                            'name': tds.name,
                            'date': date.today(),
                            'code': tds.code,
                            'partner_id': tds.partner_id.id,
                            'tds_section_id': tds.tds_section_id.id,
                            'account_id': tds.account_id.id,
                            'amount': tds.amount,
                            'tds_amount': tds.tds_amount,
                            'bal_amount': tds.bal_amount,
                            'reconcile_amount': tds.bal_amount,
                            'tds_payable': tds.tds_payable,
                        })
                        tds.unlink()
                if not tds_invoice_ids:
                    tds_invoice_id = self.env['account.tds.reconcile'].create({
                        'invoice_id': self.id,
                        'tds_payment_id': each.id,
                        'name': each.name,
                        'date': date.today(),
                        'code': each.code,
                        'partner_id': each.partner_id.id,
                        'tds_section_id': each.tds_section_id.id,
                        'account_id': each.account_id.id,
                        'amount': each.amount,
                        'tds_amount': each.tds_amount,
                        'bal_amount': each.bal_amount,
                        'reconcile_amount': each.bal_amount,
                        'tds_payable': each.tds_payable,
                    })
        for line in self.invoice_line_ids:
            base_tot_amount = tax_amount = 0.0
            if self.is_base_amount:
                base_tot_amount = line.price_unit*line.quantity
            else:
                base_tot_amount = line.price_total
            if line.price_unit <= 0:
                raise UserError(_("Enter Valid Payment Amount."))
            if line.is_apply:
                tds = sur = tax = 0.00
                tds = base_tot_amount*(self.tds_section_id.tds_percentage/100)
                sur = base_tot_amount*(self.tds_section_id.sur_percentage/100)
                tax = tds+sur
                residual += tax
                tds_invoice_line_id = self.env['account.tds.payment'].search([('invoice_line_id','=',line.id)])
                if tds_invoice_line_id:
                    tds_invoice_line_id.write({
                        'invoice_id': self.id,
                        'invoice_line_id': line.id,
                        'date': date.today(),
                        'code': self.tds_section_id.code,
                        'tds_deduct': self.is_tds,
                        'partner_id': self.partner_id.id,
                        'tds_section_id': self.tds_section_id.id,
                        'account_id': self.tds_section_id.account_id.id,
                        'amount': base_tot_amount,
                        'tds_amount': tax,
                        'tds_amount_residual': tax,
                        'bal_amount': tax,
                        'tds_payable': base_tot_amount-tax,
                        'state': 'draft',
                    })
                    tds_invoice_line_line_id = self.env['account.tds.payment.line'].search([('payment_line_id','=',tds_invoice_line_id.id)])
                    if tds_invoice_line_line_id:
                        for tds_invoice in tds_invoice_line_line_id:
                            tds_invoice.unlink()
                        tds_invoice_line_line_id.create({
                            'payment_line_id': tds_invoice_line_id.id,
                            'tax_type': 'tds',
                            'credit': tds,
                            'debit': 0,
                            'rate': self.tds_section_id.tds_percentage,
                            'base': tds_invoice_line_id.amount})
                        tds_invoice_line_line_id.create({
                            'payment_line_id': tds_invoice_line_id.id,
                            'tax_type': 'sur',
                            'credit': sur,
                            'debit': 0,
                            'rate': self.tds_section_id.sur_percentage,
                            'base': tds_invoice_line_id.amount,
                        })
                    line.is_gen = True
                else:
                    tds_invoice_line_id = self.env['account.tds.payment'].create({
                        'invoice_id': self.id,
                        'invoice_line_id': line.id,
                        'date': date.today(),
                        'code': self.tds_section_id.code,
                        'tds_deduct': self.is_tds,
                        'partner_id': self.partner_id.id,
                        'tds_section_id': self.tds_section_id.id,
                        'account_id': self.tds_section_id.account_id.id,
                        'amount': base_tot_amount,
                        'tds_amount': tax,
                        'tds_amount_residual': tax,
                        'bal_amount': tax,
                        'tds_payable': base_tot_amount-tax,
                        'state': 'draft',
                    })
                    if tds_invoice_line_id:
                        tds_invoice_line_line_id = self.env['account.tds.payment.line']
                        tds_invoice_line_line_id.create({
                            'payment_line_id': tds_invoice_line_id.id,
                            'tax_type': 'tds',
                            'credit': tds,
                            'debit': 0,
                            'rate': self.tds_section_id.tds_percentage,
                            'base': tds_invoice_line_id.amount})
                        tds_invoice_line_line_id.create({
                            'payment_line_id': tds_invoice_line_id.id,
                            'tax_type': 'sur',
                            'credit': sur,
                            'debit': 0,
                            'rate': self.tds_section_id.sur_percentage,
                            'base': tds_invoice_line_id.amount,
                        })
                    line.is_gen = True
        self.amount_tds_residual = residual   
                
    @api.multi
    def action_move_create(self):
        account_move = self.env['account.move']
        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write({'date_invoice': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.with_context(ctx).write({'date_due': inv.date_invoice})
            company_currency = inv.company_id.currency_id

            iml = inv.invoice_line_move_line_get()
            if inv.amount_tds>0:
                iml += inv.invoice_line_move_line_tds_get()
            iml += inv.tax_line_move_line_get()
            diff_currency = inv.currency_id != company_currency
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)
            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.date_invoice)[0]
                res_amount_currency = total_currency
                ctx['date'] = inv._get_currency_rate_date()
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency
                    iml.append({
                        'type': 'src',
                        'name': name,
                        'price': t[1]+inv.amount_tds,
                        'account_id': inv.account_id.id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency and amount_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'invoice_id': inv.id
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': inv.account_id.id,
                    'date_maturity': inv.date_due,
                    'amount_currency': diff_currency and total_currency,
                    'currency_id': diff_currency and inv.currency_id.id,
                    'invoice_id': inv.id
                })
            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)
            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)
            date = inv.date or inv.date_invoice
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            if self.journal_id.round_up:
                self.set_balance_amount(move)
            move.post()
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True
    
    @api.model
    def invoice_line_move_line_tds_get(self):
        res = []
        for line in self.invoice_line_ids:
            if line.is_apply:
                if line.quantity==0:
                    continue
                tax_ids = []
                for tax in line.invoice_line_tax_ids:
                    tax_ids.append((4, tax.id, None))
                    for child in tax.children_tax_ids:
                        if child.type_tax_use != 'none':
                            tax_ids.append((4, child.id, None))
                analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]
                move_line_dict = {
                    'invl_id': line.id,
                    'type': 'src',
                    'name': line.name.split('\n')[0][:64],
                    'price': -(line.bal_amount),
                    'account_id': line.invoice_id.tds_section_id.account_id.id,
                    'account_analytic_id': line.account_analytic_id.id,
                    'invoice_id': self.id,
                }
                res.append(move_line_dict)
            return res
    
    @api.model
    def invoice_line_move_line_get(self):
        res = []
        for line in self.invoice_line_ids:
            if line.quantity==0:
                continue
            tax_ids = []
            for tax in line.invoice_line_tax_ids:
                tax_ids.append((4, tax.id, None))
                for child in tax.children_tax_ids:
                    if child.type_tax_use != 'none':
                        tax_ids.append((4, child.id, None))
            analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in line.analytic_tag_ids]

            move_line_dict = {
                'invl_id': line.id,
                'type': 'src',
                'name': line.name.split('\n')[0][:64],
                'price_unit': line.price_unit,
                'quantity': line.quantity,
                'price': line.price_subtotal,
                'account_id': line.account_id.id,
                'product_id': line.product_id.id,
                'uom_id': line.uom_id.id,
                'account_analytic_id': line.account_analytic_id.id,
                'tax_ids': tax_ids,
                'invoice_id': self.id,
                'analytic_tag_ids': analytic_tag_ids
            }
            res.append(move_line_dict)
        return res
    
    @api.multi
    def register_payment(self, payment_line, writeoff_acc_id=False, writeoff_journal_id=False, invoice_type=False):
        line_to_reconcile = self.env['account.move.line']
        for inv in self:
            line_to_reconcile += inv.move_id.line_ids.filtered(lambda r: not r.reconciled and r.account_id.internal_type in ('payable', 'receivable'))
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id, invoice_type=invoice_type, invoice=self)
    
class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    is_gen = fields.Boolean('Gen', default=False)
    is_apply = fields.Boolean('Apply TDS ?')
    tds_invoice_ids = fields.One2many('account.tds.payment','invoice_line_id')
    amount_tds = fields.Monetary('TDS Amount', store=True, compute='_compute_tds_amount', readonly=True)
    bal_amount = fields.Monetary('Balance Amount', store=True, compute='_compute_tds_amount', readonly=True)
    
    @api.depends('tds_invoice_ids.tds_amount','tds_invoice_ids.bal_amount')
    def _compute_tds_amount(self):
        for val in self:
            amt_total = bal_amt = 0.00
            for line in val.tds_invoice_ids:
                amt_total += line.tds_amount
                bal_amt += line.bal_amount
            val.amount_tds = amt_total
            val.bal_amount = bal_amt
