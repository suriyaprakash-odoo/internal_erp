# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date

class TdsPayment(models.Model):
    _name = 'tds.payment'
    _description = 'TDS Payment'
    _inherit = ['mail.thread']
    
    name = fields.Char(readonly=True, copy=False, default="Draft Payment", track_visibility='always')
    partner_id = fields.Many2one('res.partner', string="Partner", domain=[('supplier', '=', True)], track_visibility='always')
    amount = fields.Monetary('Payment Amount', copy=False, track_visibility='always')
    amount_total = fields.Monetary('Total Amount', store=True, compute='_compute_amount', readonly=True, copy=False)
    journal_id = fields.Many2one("account.journal", string="Payment Journal", readonly=True, copy=False, track_visibility='always')
    payment_date = fields.Date("Payment Date", copy=False, default=date.today(), track_visibility='always')
    company_id = fields.Many2one('res.company', string="Company", readonly=True, track_visibility='always')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id, track_visibility='always')
    communication = fields.Char("Memo", copy=False, track_visibility='always')
    state = fields.Selection([('draft', "Draft"), ('posted', "Posted"), ('cancel', "Cancelled")], default="draft", copy=False, track_visibility='always')
    account_move_id = fields.Many2one("account.move", string="Journal", readonly=True, copy=False, track_visibility='always')
    note = fields.Text("Internal Notes", copy=False, track_visibility='always')
    payment_line_ids = fields.One2many('tds.payment.line', 'tds_payment_id', readonly=True, copy=False, track_visibility='always')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', oldname="payment_method", copy=False, track_visibility='always')
    payment_id = fields.Many2one('account.payment', string='Payment', copy=False)
    journal_entries_counts = fields.Integer(compute="_compute_journal_entries_counts", string='Journal Entries', copy=False, default=0)
    challan_no = fields.Char(string='Challan No.', readonly=True, track_visibility='always')
    hide_payment_method = fields.Boolean(compute='_compute_hide_payment_method',
        help="Technical field used to hide the payment method if the selected journal has only one available which is 'manual'")
    check_number_hide = fields.Boolean('check_number_hide')
    check_number = fields.Char('Check Number')
    is_payment_line = fields.Boolean(default=False)

    @api.multi
    @api.depends('journal_id')
    def _compute_hide_payment_method(self):
        for payment in self:
            if not payment.journal_id:
                payment.hide_payment_method = True
                continue
            journal_payment_methods = payment.journal_id.outbound_payment_method_ids
            payment.hide_payment_method = len(journal_payment_methods) == 1 and journal_payment_methods[0].code == 'manual'

    @api.onchange('journal_id')
    def _onchange_journal(self):
        if self.journal_id:
            self.currency_id = self.journal_id.currency_id or self.company_id.currency_id
            # Set default payment method (we consider the first to be the default one)
            payment_methods = self.journal_id.outbound_payment_method_ids
            self.payment_method_id = payment_methods and payment_methods[0] or False
            # Set payment method domain (restrict to methods enabled for the journal and to selected payment type)
            payment_type = 'outbound'
            if self.journal_id.check_manual_sequencing:
                self.check_number = self.journal_id.check_next_number
            else:
                self.check_number = ''
            return {'domain': {'payment_method_id': [('payment_type', '=', payment_type), ('id', 'in', payment_methods.ids)]}}
        return {}

    @api.onchange('payment_method_id')
    def _onchange_payment_method(self):
        if self.journal_id:
            print(self.payment_method_id.code,'asdgjknfg')
            if self.payment_method_id.code == 'check_printing':
                if self.journal_id.check_manual_sequencing:
                    self.check_number = self.journal_id.check_next_number
                else:
                    self.check_number = ''
                self.check_number_hide = False
            else:
                self.check_number_hide = True

    @api.multi
    def action_challan_number_update(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        context.update({'act_id':self.id})
        return {
            'name': _('Challan number Update'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tds.payment.wizard',
            'context': context,
            'target': 'new'
        }
    
    @api.multi
    def generate_payments(self):
        self.ensure_one()
        context = dict(self.env.context or {})
        context.update({'act_id':self.id,'journal_id':self.journal_id.id})
        return {
            'name': _('Generate Payment'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'tds.helper',
            'context': context,
            'target': 'new'
        }

    @api.depends('payment_line_ids.amount_reconcile')
    def _compute_amount(self):
        for val in self:
            amt_total = 0.00
            for line in val.payment_line_ids:
                if line.is_check:
                    amt_total += line.amount_reconcile
            val.amount_total = amt_total
            val.amount = amt_total
            
    def get_all_payment_vals(self):
        return{
            'journal_id': self.journal_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'payment_type': 'outbound',
            'amount': self.amount_total,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': 'supplier',
            'payment_method_id': self.payment_method_id.id
            }        
    
    @api.multi
    def cancel_payment(self):
        for rec in self:
            for line in self.env['account.move.line'].search([('payment_id','=',rec.payment_id.id),('credit', '>', 0)]):
                line.remove_move_reconcile()
            rec.payment_id.cancel()
            rec.payment_id.unlink()
            for line in self.env['account.move.line'].search([('move_id','=',rec.account_move_id.id),('debit', '>', 0)]):
                line.remove_move_reconcile()
            rec.account_move_id.button_cancel()
            rec.account_move_id.unlink()
            rec.state = 'cancel'
            
    @api.multi
    def reset_to_draft(self):
        return self.write({'state': 'draft'})
    
    @api.multi
    def action_create_payment(self):
        if not self.payment_method_id:
            raise UserError(_('Select payment method type.'))
        if not self.payment_line_ids:
            raise UserError(_('Create some payment details.'))
        if self.amount!=self.amount_total:
            raise UserError(_('Value entered does not equal the Payment Amount!'))
        for line in self.payment_line_ids:
            if line.is_check:
                if line.amount_reconcile > line.amount_unreconcile:
                    raise UserError(_('Value entered is more than the TDS value!'))
                else:
                    line.acc_tds_payment_id.tds_amount_residual = line.acc_tds_payment_id.tds_amount_residual - line.amount_reconcile
        journal_line = []
        payment = self.env['account.payment'].create(self.get_all_payment_vals())
        payment.post()
        self.payment_id = payment.id
        self.name = payment.name
        acc_move_id = self.env['account.move'].create({
            'date': date.today(),
            'journal_id': self.journal_id.id,
            'ref': self.name,
            'check_number':self.check_number,
            'narration': self.note,
            'line_ids': journal_line
        })
        for line in self.payment_line_ids:
            if line.amount_reconcile>0:
                debit_vals = {  
                        'tds_payment_id': self.id,
                        'account_id': line.account_id.id,
                        'partner_id': line.partner_id.id,
                        'name': self.name,
                        'debit': line.amount_reconcile,
                        'credit': 0.00,
                        'date_maturity': date.today(),
                        'company_id': self.company_id.id,
                        'move_id': acc_move_id.id
                        }
                journal_line.append((0, 0, debit_vals))
        credit_bal = {
                'tds_payment_id': self.id,
                'account_id': self.journal_id.default_credit_account_id.id,
                'partner_id': self.partner_id.id,
                'name': self.name,
                'debit': 0.00,
                'credit': self.amount_total,
                'date_maturity': date.today(),
                'company_id': self.company_id.id,
                'move_id': acc_move_id.id
                }
        journal_line.append((0, 0, credit_bal))
        acc_move_id.write({
            'line_ids': journal_line
        })
        acc_move_id.post()
        for line in self.payment_line_ids:
            move_line_pay_id = self.env['account.move.line']
            if line.acc_payment_id:
                move_line_pay_id = self.env['account.move.line'].search([('payment_id', '=', line.acc_payment_id.id),('account_id', '=', line.account_id.id), ('reconciled', '=', False), ('credit', '>', 0)])
            if line.invoice_id:                
                move_line_pay_id = self.env['account.move.line'].search([('invoice_id', '=', line.invoice_id.id), ('account_id', '=', line.account_id.id), ('reconciled', '=', False), ('credit', '>', 0)])
            move_line_id = self.env['account.move.line'].search([('move_id', '=', acc_move_id.id), ('reconciled', '=', False), ('debit', '>', 0)])
            self.trans_rec_reconcile_payment(move_line_id,move_line_pay_id)
        for line in self.payment_line_ids:
            if line.invoice_id:
                bal = line.acc_tds_payment_id.bal_amount - line.amount_reconcile
                line.acc_tds_payment_id.bal_amount = bal
                if bal == 0.0:
                    line.acc_tds_payment_id.state = 'paid'
            if line.acc_payment_id:
                bal = line.acc_tds_payment_id.payment_bal_amount - line.amount_reconcile
                line.acc_tds_payment_id.payment_bal_amount = bal
                if bal == 0.0:
                    line.acc_tds_payment_id.state = 'paid'
        return self.write({'state': 'posted','account_move_id': acc_move_id.id})
    
    @api.multi
    def trans_rec_reconcile_payment(self,line_to_reconcile,payment_line,writeoff_acc_id=False,writeoff_journal_id=False):
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)
    
    @api.multi
    def _compute_journal_entries_counts(self):
        journal_id = self.env['account.move'].search([('ref', '=', self.name)])
        if journal_id:
            self.journal_entries_counts = len(journal_id)
            
    @api.multi
    def action_view_journal_entries(self):
        journal_id = self.env['account.move'].search([('ref', '=', self.name)]).ids
        action = self.env.ref('account.action_move_journal_line').read()[0]
        if journal_id:
            action['domain'] = [('id', 'in', journal_id)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
    
class TdsPaymentLine(models.Model):
    _name = 'tds.payment.line'
    _description = 'TDS Payment Line'
    
    name = fields.Char('Reference')
    partner_id = fields.Many2one('res.partner', string="Partner", domain=[('supplier', '=', True)], required=True)
    tds_payment_id = fields.Many2one('tds.payment', string="Payment")
    acc_tds_payment_id = fields.Many2one('account.tds.payment')
    acc_payment_id = fields.Many2one('account.payment')
    invoice_id = fields.Many2one('account.invoice')
    amount = fields.Float('TDS Amount', default=0.00)
    amount_unreconcile = fields.Float('Open Balance', default=0.00)
    amount_reconcile = fields.Float('Amount', default=0.00)
    account_id = fields.Many2one('account.account')
    payment_date = fields.Date("Payment Date")
    is_check = fields.Boolean('Needed?', default=False)
