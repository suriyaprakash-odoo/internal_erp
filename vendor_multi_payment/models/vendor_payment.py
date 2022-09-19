from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import date
import time

class VendorMultiPayment(models.Model):
    _name = "vendor.multi.payment"
    _order = 'name desc'
    _inherit = ['mail.thread']
    
    name = fields.Char("Name", default="Draft Payment", track_visibility='always')
    partner_id = fields.Many2one('res.partner', string="Partner", domain=[('supplier', '=', True)], required=True, track_visibility='always')
    paid_amount = fields.Float("Paid Amount", default=0.00, track_visibility='always')
    debit_amount = fields.Float("Debit Amount", compute='_compute_amount')
    journal_id = fields.Many2one("account.journal", string="Payment Journal", domain=[('type', 'in', ('bank', 'cash'))], track_visibility='always')
    payment_mode_id = fields.Many2one("ppts.payment.mode.master", string="Payment Mode", track_visibility='always')
    payment_date = fields.Date("Payment Date", default=lambda self: fields.Datetime.now(), track_visibility='always')
    communication = fields.Char("Memo", track_visibility='always')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id, track_visibility='always')
    debit_line_ids = fields.One2many('vendor.multi.payment.line', 'multi_pay_id', string="Debit Line", domain=[('invoice_id.type', '=', 'in_invoice')])
    credit_line_ids = fields.One2many('vendor.multi.payment.line', 'multi_pay_id', string="Credit Line", domain=[('invoice_id.type', '=', 'in_refund')])
    state = fields.Selection([('draft', "Draft"), ('posted', "Posted"), ('cancel', "Cancel")], default="draft", track_visibility='always')
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money'), ('transfer', "Transfer")], string='Payment Type')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True, oldname="payment_method",
                                        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n" \
                                             "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n" \
                                             "Check: Pay bill by check and print it from Odoo.\n" \
                                             "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit,module account_batch_deposit must be installed.\n" \
                                             "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])
    note = fields.Text("Internal Notes")
    account_move_id = fields.Many2one("account.move", string="Journal Entry", copy=False, track_visibility='always')
    challan_no = fields.Char(string='Challan No.', readonly=True)
    currency_rate = fields.Float('Currency Rate', track_visibility='always')
    payment_difference = fields.Float(string="Payment Difference", copy=False, store=True, compute='_compute_amount', readonly=True, track_visibility='always')
    writeoff_account_id = fields.Many2one('account.account', string="Difference Account", domain=[('deprecated', '=', False)], copy=False)
    writeoff_label = fields.Char(
        string='Journal Item Label',
        help='Change label of the counterpart that will hold the payment difference',
        default='Write-Off')
    
    @api.depends('paid_amount','debit_line_ids.amount_to_pay','credit_line_ids.amount_to_pay')
    def _compute_amount(self):
        for val in self:
            credit = debit = 0.00
            credit = sum(line.amount_to_pay for line in self.credit_line_ids)
            debit = sum(line.amount_to_pay for line in self.debit_line_ids)
            val.debit_amount = debit - credit
            val.payment_difference = val.debit_amount - val.paid_amount
        
    @api.onchange('journal_id')
    def onchange_journal_id(self):
        if self.journal_id:
            if self.journal_id.inbound_payment_method_ids:
                self.payment_method_id = self.journal_id.inbound_payment_method_ids[0].id
            if self.journal_id.currency_id.id:
                self.currency_id = self.journal_id.currency_id.id
            else:
                self.currency_id = self.env.user.company_id.currency_id.id

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        if self.partner_id:
            invoice_ids = self.env['account.invoice'].search([('partner_id', '=', self.partner_id.id), ('state', '=', 'open')])
            total_amount = 0.0
            if not invoice_ids:
                self.credit_line_ids = False
                self.debit_line_ids = False
            credit_lines = []
            debit_lines = []
            for inv in invoice_ids:
                total_amount += inv.residual
                line_vals = {
                    'description': inv.vendor_invoice or False,
                    'amount_invoice': inv.amount_total or False,
                    'amount_residual': inv.residual or False,
                    'invoice_id': inv.id,
                    'invoice_date': inv.date_invoice or '',
                    'currency_id': inv.currency_id.id,
                }
                if inv.type == 'in_invoice':
                    debit_lines.append((0, 0, line_vals))
                elif inv.type == 'in_refund':
                    credit_lines.append((0, 0, line_vals))
            self.debit_line_ids = debit_lines
            self.credit_line_ids = credit_lines
            self.paid_amount = total_amount

    def get_all_payment_vals(self):
        # if self.credit_line_ids[0].currency_id.rate > 0.00:
#         if self.debit_line_ids[0].currency_rate > 0.00:
            # amount_to_pay = self.paid_amount / self.credit_line_ids[0].currency_id.rate
        if abs(self.payment_difference) != 0.00: 
            amount_to_pay = self.paid_amount + abs(self.payment_difference)
        else:
            amount_to_pay = self.paid_amount
        lines = []
        for line in self.debit_line_ids:
            lines.append(line.invoice_id)
        for line in self.credit_line_ids:
            lines.append(line.invoice_id)

        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'invoice_ids': [(6, 0, [x.id for x in lines])],
            'payment_type': self.payment_type,
            'amount': amount_to_pay,
            'currency_id': self.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': self.partner_type,
            'currency_rate': self.debit_line_ids[0].currency_rate,
            'payment_mode_id': self.payment_mode_id.id,
            'note': self.note,
#             'payment_difference':self.payment_difference,
#             'payment_difference_handling':self.payment_difference_handling,
#             'writeoff_account_id':self.writeoff_account_id.id,
#             'writeoff_label':self.writeoff_label
        }
        
    @api.multi
    def cancel_payment(self):
        payment_id = self.env["account.payment"].search([('name', '=', self.name)])
        if payment_id:
            for move in payment_id.move_line_ids.mapped('move_id'):
                if payment_id.invoice_ids:
                    move.line_ids.remove_move_reconcile()
                move.button_cancel()
                move.unlink()
            payment_id.state = 'cancelled'
        self.state = 'cancel'

    @api.multi
    def reset_to_draft(self):
        self.state = 'draft'

    @api.multi
    def create_payments(self):
        ctx = self._context.copy()
        if self.paid_amount > round(sum(line.amount_invoice for line in self.debit_line_ids), 4):
            raise UserError(_("Payment amount exceeds Invoice Amount"))

        if self.paid_amount == 0.0 and round(sum(line.amount_to_pay for line in self.debit_line_ids), 4) == 0.0:
            raise UserError(_("Please add some amount to process the invoices"))

        credit = sum(line.amount_to_pay for line in self.credit_line_ids)
        debit = sum(line.amount_to_pay for line in self.debit_line_ids)
        diff = self.debit_amount - self.paid_amount
        
        for line in self.debit_line_ids:
            if not line.amount_to_pay: 
                raise UserError(_(" Please add some amount to Debit lines"))
            
        if (self.debit_amount) != (self.paid_amount + diff):
            raise UserError(_("Payment amount exceeds Amount to pay"))

        for line in self.credit_line_ids:
            if line.amount_invoice < line.amount_to_pay:
                raise UserError(_("Amount to pay exceeds Invoice amount"))

        for line in self.debit_line_ids:
            if line.amount_invoice < line.amount_to_pay:
                raise UserError(_("Amount to pay exceeds Invoice amount"))

        if self.credit_line_ids or self.debit_line_ids:
            payment = self.env['account.payment'].create(self.get_all_payment_vals())
            payment.ven_multi_pay_id = self.id
            split_payment = []
            for i in self.credit_line_ids:
                if i.amount_to_pay != 0.0:
                    split_payment.append({i.invoice_id: -(i.amount_to_pay)})
            for i in self.debit_line_ids:
                if i.amount_to_pay != 0.0:
                    split_payment.append({i.invoice_id: (i.amount_to_pay)})
            if self.payment_difference:
                amount = list(split_payment[0].values())[0]
                val = amount - self.payment_difference
                split_payment.append({list(split_payment[0].keys())[0]: (val)})
                split_payment.remove({list(split_payment[0].keys())[0]: (list(split_payment[0].values())[0])})
            ctx.update({'split_payment': split_payment})
            payment.with_context(ctx).post()
            move_line_id = self.env['account.move.line'].search([('payment_id', '=', payment.id)])
            if move_line_id:
                self.account_move_id = move_line_id[0].move_id.id
            self.name = payment.name
            self.state = 'posted'
        for line in self.credit_line_ids:
            inv_ids = self.env['account.invoice'].search([('id', '=', line.invoice_id.id)])
            if inv_ids:
                inv_ids.challan_no = line.challan_no
        for line in self.debit_line_ids:
            inv_ids = self.env['account.invoice'].search([('id', '=', line.invoice_id.id)])
            if inv_ids:
                inv_ids.challan_no = line.challan_no
        return True

    @api.multi
    def open_journal_entries(self):
        payment_ids = self.env["account.move.line"].search([('payment_id.name', '=', self.name)])
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in payment_ids])],
        }

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
            'res_model': 'vendor.multi.payment.wizard',
            'context': context,
            'target': 'new'
        }
        
        
class VendorPaymentLine(models.Model):
    _name = "vendor.multi.payment.line"

    description = fields.Char('Vendor Invoice')
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    amount_invoice = fields.Float('Bill Amount')
    amount_residual = fields.Float('Residual')
    amount_invoice_dup = fields.Float(related='amount_invoice', string='Bill Amount', store=True)
    amount_residual_dup = fields.Float(related='amount_residual', string='Residual', store=True)
    inverse_val = fields.Float('Inverse Value', digits=(12, 6))
    invoice_date = fields.Date('Bill Date')
    amount_to_pay = fields.Float('Amount to pay', default=0.00)
    full_reconcile = fields.Boolean('Full Reconcile')
    currency_id = fields.Many2one('res.currency', string='Currency')
    challan_no = fields.Char(string='Challan No.', readonly=True)
    multi_pay_id = fields.Many2one("vendor.multi.payment", "Payment ID")
    currency_rate = fields.Float('Currency Rate', related='multi_pay_id.currency_rate', readonly = True)

    @api.onchange('full_reconcile')
    def onchange_full_reconcile(self):
        if self.full_reconcile:
            self.amount_to_pay = self.amount_residual
        else:
            self.amount_to_pay = 0.0

    @api.model
    def create(self, vals):
        if vals.get('amount_invoice'):
            vals['amount_invoice'] = vals.get('amount_invoice')
        if vals.get('amount_residual'):
            vals['amount_residual'] = vals.get('amount_residual')
        return super(VendorPaymentLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('amount_invoice'):
            vals['amount_invoice'] = vals.get('amount_invoice')
        if vals.get('amount_residual'):
            vals['amount_residual'] = vals.get('amount_residual')
        return super(VendorPaymentLine, self).write(vals)

class AccountMove(models.Model):
    _inherit = "account.move"
    
    challan_no = fields.Char(string='Challan No.', readonly=True)
    
class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    ven_multi_pay_id = fields.Many2one("vendor.multi.payment", "Payment ID")
    
    # multi vendor bills fully paid
    def _get_shared_move_line_vals_inherit(self, credit, debit, amount_currency, move_id, invoice_id=False):
        return {
            'account_id': self.ven_multi_pay_id.writeoff_account_id.id,
            'partner_id': self.ven_multi_pay_id.partner_id.id,
            'name': self.ven_multi_pay_id.writeoff_label,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency or False,
            'currency_id': self.currency_id.id,
            'payment_id': self.id,
            'move_id': move_id
        }
        
    def _create_payment_entry(self, amount):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)

        move_vals = self._get_move_vals()
        move_vals['payment_mode_id'] = self.payment_mode_id.id
        
        move = self.env['account.move'].create(move_vals)
        if not self._context.get('split_payment'):
            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount,self.currency_id,self.company_id.currency_id)
            counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
            counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
            counterpart_aml_dict.update({'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False})
            if self.currency_rate:
                current_amt = self.currency_rate * counterpart_aml_dict['amount_currency']
                if current_amt < 0:
                    current_amt = current_amt * -1
                counterpart_aml_dict.update({'credit': current_amt})
            #Round off Credit and debit amount by jana
            journal_vals = self.env['account.journal'].search_read([('id','=',self.journal_id.id)],limit=1)[0]
            if journal_vals.get('round_up', False):
                counterpart_aml_dict.update({'debit':round(counterpart_aml_dict.get('debit',0)),'credit':round(counterpart_aml_dict.get('credit',0))})

            counterpart_aml = aml_obj.create(counterpart_aml_dict)
            
            # Write counterpart lines
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            if self.currency_rate:
                current_amt = self.currency_rate * counterpart_aml_dict['amount_currency']
                if current_amt < 0:
                    current_amt = current_amt * -1
                liquidity_aml_dict.update({'debit': current_amt})

            #Round off Credit and debit amount by jana
            if journal_vals.get('round_up', False):
                liquidity_aml_dict.update({'debit':round(liquidity_aml_dict.get('debit',0)),'credit':round(liquidity_aml_dict.get('credit',0))})
            aml_obj.create(liquidity_aml_dict)
            
            if self.payment_difference_handling == 'reconcile':
                self.invoice_ids.register_payment(counterpart_aml, self.writeoff_account_id, self.journal_id)
            else:
                self.invoice_ids.register_payment(counterpart_aml)

        elif self._context.get('split_payment'):

            for loop in self._context['split_payment']:
                invoice_ids = list(loop.keys())[0]
                loop_amount = list(loop.values())[0]
                debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(loop_amount,self.currency_id,self.company_id.currency_id)
                counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
                counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_ids))
                counterpart_aml_dict.update({'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False})

                if self.currency_rate:
                    current_amt = self.currency_rate * counterpart_aml_dict['amount_currency']
                    if current_amt < 0:
                        current_amt = current_amt * -1
                    counterpart_aml_dict.update({'credit': current_amt})

                #Round off Credit and debit amount by jana
                journal_vals = self.env['account.journal'].search_read([('id','=',self.journal_id.id)],limit=1)[0]
                if journal_vals.get('round_up', False):
                    counterpart_aml_dict.update({'debit':round(counterpart_aml_dict.get('debit',0)),'credit':round(counterpart_aml_dict.get('credit',0))})
                
                counterpart_aml = aml_obj.create(counterpart_aml_dict)
                if not self.ven_multi_pay_id and  not self.cus_multi_pay_id:
                    if self.payment_difference_handling == 'reconcile':
                        invoice_ids.register_payment(counterpart_aml, self.writeoff_account_id, self.journal_id)
                    else:
                        invoice_ids.register_payment(counterpart_aml)
            # Write counterpart lines
            debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount,self.currency_id,self.company_id.currency_id)
            
            # multi vendor bills fully paid
            if debit and self.ven_multi_pay_id:
                diff = self.ven_multi_pay_id.debit_amount - self.ven_multi_pay_id.paid_amount
                if diff > 0.0:
                    diff_amt, cre, amount_cur, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(diff,self.currency_id,self.company_id.currency_id)
                    debit = debit - diff_amt
                    debit_amt = diff_amt
                    counterpart_aml_dict_inh = self._get_shared_move_line_vals_inherit(diff_amt, credit, amount_cur, move.id, False)
                    if amount_cur:
                        amount_currency = amount_currency + amount_cur
                        if self.currency_rate:
                            current_amt = self.currency_rate * amount_cur
                        else:
                            rate_id = self.env['res.currency'].search([('id','=',self.ven_multi_pay_id.currency_id.id)])
                            current_amt = (1/rate_id.rate) * amount_cur
                        debit_amt = current_amt
                        counterpart_aml_dict_inh.update({'credit': current_amt})
                    counterpart_aml_ven = aml_obj.create(counterpart_aml_dict_inh)
                    am = aml_obj.create({
                        'name': _('Vendor Payment'),
                        'debit': debit_amt,
                        'credit': 0.0,
                        'account_id': move.partner_id.property_account_payable_id.id,
                        'move_id': move.id,
                        'currency_id': self.currency_id.id,
                        'amount_currency': amount_cur or False,
                        'partner_id': move.partner_id.id,
                        'payment_id': self.id,
                    })
            # multi customer invoice fully paid
            if credit and self.cus_multi_pay_id:
                diff = self.cus_multi_pay_id.credit_amount - self.cus_multi_pay_id.paid_amount
                if diff > 0.0:
                    diff_amt, cre, amount_cur, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(diff,self.currency_id,self.company_id.currency_id)
                    credit = credit - diff_amt
                    debit_amt = diff_amt
                    counterpart_aml_dict_inh = self._get_shared_move_line_vals_cus_inherit(diff_amt, debit, amount_cur, move.id, False)
                    if amount_cur:
                        amount_currency = amount_currency + amount_cur
                        if self.currency_rate:
                            current_amt = self.currency_rate * amount_cur
                        else:
                            rate_id = self.env['res.currency'].search([('id','=',self.cus_multi_pay_id.currency_id.id)])
                            current_amt = (1/rate_id.rate) * amount_cur
                        debit_amt = current_amt
                        counterpart_aml_dict_inh.update({'debit': current_amt})
                    counterpart_aml_inh = aml_obj.create(counterpart_aml_dict_inh)
                    am = aml_obj.create({
                        'name': _('Customer Payment'),
                        'debit': 0.0,
                        'credit': debit_amt,
                        'account_id': move.partner_id.property_account_receivable_id.id,
                        'move_id': move.id,
                        'currency_id': self.currency_id.id,
                        'amount_currency': amount_cur or False,
                        'partner_id': move.partner_id.id,
                        'payment_id': self.id,
                    })
                    
            liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
            liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
            if self.currency_rate:
                current_amt = self.currency_rate * liquidity_aml_dict['amount_currency']
                if current_amt < 0:
                    current_amt = current_amt * -1
                liquidity_aml_dict.update({'debit': current_amt})
                
            #Round off Credit and debit amount by jana
            if journal_vals.get('round_up', False):
                liquidity_aml_dict.update({'debit':round(liquidity_aml_dict.get('debit',0)),'credit':round(liquidity_aml_dict.get('credit',0))})
            aml_obj.create(liquidity_aml_dict)
            
            if self.ven_multi_pay_id:
                for loop in self._context['split_payment']:
                    invoice_id = list(loop.keys())[0]
                    move_line_invoice_id = self.env['account.move.line'].search([('invoice_id', '=', invoice_id.id), ('reconciled', '=', False), ('credit', '>', 0)])
                    move_line_payment_id = self.env['account.move.line'].search([('payment_id', '=', self.id), ('reconciled', '=', False), ('debit', '>', 0)])
                    self.trans_rec_reconcile_payment(move_line_payment_id,move_line_invoice_id)
            if self.cus_multi_pay_id:
                for loop in self._context['split_payment']:
                    invoice_id = list(loop.keys())[0]
                    move_line_invoice_id = self.env['account.move.line'].search([('invoice_id', '=', invoice_id.id), ('reconciled', '=', False), ('debit', '>', 0)])
                    move_line_payment_id = self.env['account.move.line'].search([('payment_id', '=', self.id), ('reconciled', '=', False), ('credit', '>', 0)])
                    self.trans_rec_reconcile_payment(move_line_payment_id,move_line_invoice_id)
             
        move.post()
        return move
    
    @api.multi
    def trans_rec_reconcile_payment(self,line_to_reconcile,payment_line,writeoff_acc_id=False,writeoff_journal_id=False):
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)
    
class AccountPartialReconcile(models.Model):
    _inherit = "account.partial.reconcile"

    @api.model
    def create_exchange_rate_entry(self, aml_to_fix, amount_diff, diff_in_currency, currency, move):
        move_line = self.env['account.move.line'].search([('move_id','=', move.id)])
        if move_line[0].payment_id.ven_multi_pay_id or move_line[0].payment_id.cus_multi_pay_id:
            partial_rec = self.env['account.partial.reconcile']
            aml_model = self.env['account.move.line']
            account_id_rec = self.env['account.account']
            currency_amount = credit_amount_diff = debit_amount_diff = diff = 0.0
            amount_diff = move.company_id.currency_id.round(amount_diff)
            if move_line[0].payment_id.ven_multi_pay_id:
                diff = move_line[0].payment_id.ven_multi_pay_id.debit_amount - move_line[0].payment_id.ven_multi_pay_id.paid_amount 
                rate = move_line[0].payment_id.ven_multi_pay_id.debit_line_ids[0].currency_rate
                debit_amount_diff = diff * rate 
                account_id_rec = move_line[0].payment_id.ven_multi_pay_id.writeoff_account_id.id
                account_id_rec_partner = move_line[0].payment_id.ven_multi_pay_id.partner_id.property_account_receivable_id.id
            if move_line[0].payment_id.cus_multi_pay_id:
                diff = move_line[0].payment_id.cus_multi_pay_id.credit_amount - move_line[0].payment_id.cus_multi_pay_id.paid_amount
                rate = move_line[0].payment_id.cus_multi_pay_id.credit_line_ids[0].currency_rate
                credit_amount_diff = diff * rate 
                account_id_rec = move_line[0].payment_id.cus_multi_pay_id.writeoff_account_id.id
                account_id_rec_partner = move_line[0].payment_id.cus_multi_pay_id.partner_id.property_account_receivable_id.id
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
                
                line_to = aml_model.with_context(check_move_validity=False).create({
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
                
#                 Writeoff For ex gain and loss

#                 if diff > 0.0:
# #                     if move_line[0].payment_id.ven_multi_pay_id:
# #                         line_to_rec.debit = line_to.debit - debit_amount_diff
# #                     if move_line[0].payment_id.cus_multi_pay_id: 
# #                         line_to.credit = line_to.credit - credit_amount_diff
#                     aml_model.with_context(check_move_validity=False).create({
#                         'name': _('Currency exchange rate difference'),
#                         'debit': debit_amount_diff or 0.0,
#                         'credit': credit_amount_diff or 0.0,
#                         # 'account_id': amount_diff > 0 and exchange_journal.default_debit_account_id.id or exchange_journal.default_credit_account_id.id,
#                         'account_id': account_id_rec,
#                         'move_id': move.id,
#                         'currency_id': currency.id,
#                         'amount_currency': diff_in_currency and aml.amount_residual_currency or 0.0,
#                         'partner_id': aml.partner_id.id,
#                         'exchange_flag': True,
#                     })
#                     aml_model.with_context(check_move_validity=False).create({
#                         'name': _('Currency exchange rate difference'),
#                         'debit': credit_amount_diff or 0.0,
#                         'credit': debit_amount_diff or 0.0,
#                         # 'account_id': amount_diff > 0 and exchange_journal.default_debit_account_id.id or exchange_journal.default_credit_account_id.id,
#                         'account_id': account_id_rec_partner,
#                         'move_id': move.id,
#                         'currency_id': currency.id,
#                         'amount_currency': diff_in_currency and aml.amount_residual_currency or 0.0,
#                         'partner_id': aml.partner_id.id,
#                         'exchange_flag': True,
#                     })
        
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
        else:
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

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    
    def _create_writeoff(self, vals):
        amount_currency = 0
        # Check and complete vals
        if 'account_id' not in vals or 'journal_id' not in vals:
            raise UserError(_("It is mandatory to specify an account and a journal to create a write-off."))
        if ('debit' in vals) ^ ('credit' in vals):
            raise UserError(_("Either pass both debit and credit or none."))
        if 'date' not in vals:
            vals['date'] = self._context.get('date_p') or time.strftime('%Y-%m-%d')
        if 'name' not in vals:
            vals['name'] = self._context.get('comment') or _('Write-Off')
        if 'analytic_account_id' not in vals:
            vals['analytic_account_id'] = self.env.context.get('analytic_id', False)
        #compute the writeoff amount if not given
        if 'credit' not in vals and 'debit' not in vals:
            amount = sum([r.amount_residual for r in self])
            vals['credit'] = amount > 0 and amount or 0.0
            vals['debit'] = amount < 0 and abs(amount) or 0.0
        vals['partner_id'] = self.env['res.partner']._find_accounting_partner(self[0].partner_id).id
        company_currency = self[0].account_id.company_id.currency_id
        writeoff_currency = self[0].currency_id or company_currency
        if not self._context.get('skip_full_reconcile_check') == 'amount_currency_excluded' and 'amount_currency' not in vals and writeoff_currency != company_currency:
            vals['currency_id'] = writeoff_currency.id
            sign = 1 if vals['debit'] > 0 else -1
            vals['amount_currency'] = sign * abs(sum([r.amount_residual_currency for r in self]))
            amount_currency = sign * abs(sum([r.amount_residual_currency for r in self]))
            
        move_line = vals['move_line_id']
        rate = move_line.payment_id.currency_rate
        
        if vals['credit'] == 0 and vals['debit'] == 0:
            vals['credit'] = rate * abs(amount_currency)
        # Writeoff line in the account of self
        first_line_dict = self._prepare_writeoff_first_line_values(vals)
        # Writeoff line in specified writeoff account
        second_line_dict = self._prepare_writeoff_second_line_values(vals)

        # Create the move
        writeoff_move = self.env['account.move'].with_context(apply_taxes=True).create({
            'journal_id': vals['journal_id'],
            'date': vals['date'],
            'state': 'draft',
            'line_ids': [(0, 0, first_line_dict), (0, 0, second_line_dict)],
        })
        writeoff_move.post()

        # Return the writeoff move.line which is to be reconciled
        return writeoff_move.line_ids.filtered(lambda r: r.account_id == self[0].account_id)
    
    @api.multi
    @api.constrains('amount_currency')
    def _check_currency_amount(self):
        for line in self:
            if not line.payment_id.ven_multi_pay_id and not line.payment_id.cus_multi_pay_id:
                if line.amount_currency:
                    if (line.amount_currency > 0.0 and line.credit > 0.0) or (line.amount_currency < 0.0 and line.debit > 0.0):
                        raise ValidationError(_('The amount expressed in the secondary currency must be positive when account is debited and negative when account is credited.'))
