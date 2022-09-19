from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning

class VendorPartialPayment(models.Model):
    _name = "vendor.partial.payment"
    _order = 'name desc'

    name = fields.Char("Name", default="Draft Payment")
    partner_id = fields.Many2one('res.partner', string="Partner", domain=[('supplier', '=', True)], required=True)
    paid_amount = fields.Float("Paid Amount", default=0.00)
    journal_id = fields.Many2one("account.journal", string="Payment Journal", domain=[('type', 'in', ('bank', 'cash'))])
    payment_mode_id = fields.Many2one("ppts.payment.mode.master", string="Payment Mode")
    payment_date = fields.Date("Payment Date", default=lambda self: fields.Datetime.now())
    communication = fields.Char("Memo")
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id)
    debit_line_ids = fields.One2many('vendor.partial.payment.line', 'multi_pay_id', string="Debit Line", domain=[('invoice_id.type', '=', 'in_invoice')])
    credit_line_ids = fields.One2many('vendor.partial.payment.line', 'multi_pay_id', string="Credit Line", domain=[('payment_id.payment_type', '=', 'outbound')])
    state = fields.Selection([('draft', "Draft"), ('posted', "Posted"), ('cancel', "Cancel")], default="draft")
    payment_type = fields.Selection([('outbound', 'Send Money'), ('inbound', 'Receive Money'), ('transfer', "Transfer")], string='Payment Type')
    payment_method_id = fields.Many2one('account.payment.method', string='Payment Method Type', required=True, oldname="payment_method",
                                        help="Manual: Get paid by cash, check or any other method outside of Odoo.\n" \
                                             "Electronic: Get paid automatically through a payment acquirer by requesting a transaction on a card saved by the customer when buying or subscribing online (payment token).\n" \
                                             "Check: Pay bill by check and print it from Odoo.\n" \
                                             "Batch Deposit: Encase several customer checks at once by generating a batch deposit to submit to your bank. When encoding the bank statement in Odoo, you are suggested to reconcile the transaction with the batch deposit.To enable batch deposit,module account_batch_deposit must be installed.\n" \
                                             "SEPA Credit Transfer: Pay bill from a SEPA Credit Transfer file you submit to your bank. To enable sepa credit transfer, module account_sepa must be installed ")
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Vendor')])
    note = fields.Text("Internal Notes")
    account_move_id = fields.Many2one("account.move", string="Journal Entry")

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('vendor.partial.payment')
        return super(VendorPartialPayment, self).create(vals) 

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
                # total_amount += inv.residual
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
            payment_ids = self.env['account.payment'].search([('partner_id','=',self.partner_id.id),('state','=','posted'),('partner_type','=','supplier')])
            for pay in payment_ids:
                move_line_id = self.env['account.move.line'].search([('payment_id','=',pay.id),('reconciled','=',False),('debit', '>', 0)])
                if not pay.name in credit_lines and move_line_id:
                    line_vals_pay = {
                    'description': pay.name or False,
                    'amount_invoice': pay.amount or False,
                    'amount_residual': move_line_id.amount_residual or False,
                    'payment_id': pay.id,
                    'invoice_date': pay.payment_date or '',
                    'currency_id': pay.currency_id.id,
                    }
                    credit_lines.append((0, 0, line_vals_pay))
            self.debit_line_ids = debit_lines
            self.credit_line_ids = credit_lines
            self.paid_amount = total_amount

    def get_all_payment_vals(self):
        if self.debit_line_ids[0].currency_rate > 0.00:
            amount_to_pay = self.paid_amount
        else:
            amount_to_pay = self.paid_amount
        lines = []
        for line in self.debit_line_ids:
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
        for lines in self.credit_line_ids:
            if lines.amount_to_pay > 0:
                if lines.payment_id:
                    for move in lines.payment_id.move_line_ids.mapped('move_id'):
                        if lines.payment_id:
                            lines.reconciled = False
                            move.line_ids.remove_move_reconcile()
                        move.button_cancel()
                        move.unlink()
                    lines.payment_id.invoice_ids = False
                    lines.payment_id.state = 'cancelled'
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

        if (self.paid_amount + credit) != debit:
            raise UserError(_("Payment amount exceeds Amount to pay"))

        for line in self.credit_line_ids:
            if line.payment_id and line.amount_to_pay:
                move_line_payment_id = self.env['account.move.line'].search([('payment_id', '=', line.payment_id.id), ('reconciled', '=', False), ('debit', '>', 0)])
            if line.amount_invoice < line.amount_to_pay:
                raise UserError(_("Amount to pay exceeds Invoice amount"))

        for line in self.debit_line_ids:
            if line.amount_invoice < line.amount_to_pay:
                raise UserError(_("Amount to pay exceeds Invoice amount"))

        if self.credit_line_ids or self.debit_line_ids:
            if self.paid_amount:
                payment = self.env['account.payment'].create(self.get_all_payment_vals())
                payment.with_context(ctx).post()
                move_line_id = self.env['account.move.line'].search([('payment_id', '=', payment.id)])
                if move_line_id:
                    self.account_move_id = move_line_id[0].move_id.id
                self.name = payment.name
                move_line_payment_id = self.env['account.move.line'].search([('payment_id', '=', payment.id), ('reconciled', '=', False), ('debit', '>', 0)])
                for line in self.debit_line_ids:    
                    if line.invoice_id:                
                        move_line_invoice_id = self.env['account.move.line'].search([('invoice_id', '=', line.invoice_id.id), ('account_id', '=', line.invoice_id.account_id.id),('reconciled', '=', False), ('credit', '>', 0)])
                    self.trans_rec_reconcile_payment(move_line_payment_id,move_line_invoice_id)
            for line in self.debit_line_ids:    
                if line.invoice_id and line.amount_to_pay > 0:                
                    move_line_invoice_id = self.env['account.move.line'].search([('invoice_id', '=', line.invoice_id.id),('account_id', '=', line.invoice_id.account_id.id), ('reconciled', '=', False), ('credit', '>', 0)])
                if line.amount_to_pay > 0:
                    for lines in self.credit_line_ids:
                        if lines.payment_id and lines.amount_to_pay > 0:
                            move_line_payment_id = self.env['account.move.line'].search([('payment_id', '=', lines.payment_id.id), ('reconciled', '=', False), ('debit', '>', 0)])
                            for line_id in move_line_payment_id:
                                if line_id.partial_pay_id != lines.id:
                                    line_id.partial_pay_id = lines.id
                            self.trans_rec_reconcile_payment(move_line_payment_id,move_line_invoice_id)
            return self.write({'state': 'posted'})
        return True
    
    @api.multi
    def trans_rec_reconcile_payment(self,line_to_reconcile,payment_line,writeoff_acc_id=False,writeoff_journal_id=False):
        return (line_to_reconcile + payment_line).reconcile(writeoff_acc_id, writeoff_journal_id)

    @api.multi
    def open_journal_entries(self):
        line_ids=[]
        if self.account_move_id:
            move_line_id = self.env['account.move.line'].search([('move_id', '=', self.account_move_id.id)])
            for lines in move_line_id:
                line_ids.append(lines.id)
        for line in self.credit_line_ids:
            if line.amount_to_pay>0.00:
                move_line_id = self.env['account.move.line'].search([('payment_id', '=', line.payment_id.id)])
                for lines in move_line_id:
                    line_ids.append(lines.id)
        for line in self.debit_line_ids:
            if line.amount_to_pay>0.00:
                move_line_id = self.env['account.move.line'].search([('invoice_id', '=', line.invoice_id.id)])
                for lines in move_line_id:
                    line_ids.append(lines.id)
        payment_ids = self.env["account.move.line"].search([('id', 'in', line_ids)])
        return {
            'name': _('Journal Items'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move.line',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', [x.id for x in payment_ids])],
        }

        
class VendorPartialPaymentLine(models.Model):
    _name = "vendor.partial.payment.line"

    description = fields.Char('Vendor Invoice')
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    payment_id = fields.Many2one('account.payment', string="Payment")
    amount_invoice = fields.Float('Bill Amount')
    amount_residual = fields.Float('Residual')
    amount_invoice_dup = fields.Float(related='amount_invoice', string='Bill Amount', store=True)
    amount_residual_dup = fields.Float(related='amount_residual', string='Residual', store=True)
    inverse_val = fields.Float('Inverse Value', digits=(12, 6))
    currency_rate = fields.Float('Currency Rate')
    invoice_date = fields.Date('Bill Date')
    amount_to_pay = fields.Float('Amount to pay', default=0.00)
    full_reconcile = fields.Boolean('Full Reconcile')
    currency_id = fields.Many2one('res.currency', string='Currency')
    challan_no = fields.Char(string='Challan No.', readonly=True)
    multi_pay_id = fields.Many2one("vendor.partial.payment", "Payment ID")

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
        return super(VendorPartialPaymentLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('amount_invoice'):
            vals['amount_invoice'] = vals.get('amount_invoice')
        if vals.get('amount_residual'):
            vals['amount_residual'] = vals.get('amount_residual')
        return super(VendorPartialPaymentLine, self).write(vals)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    partial_pay_id = fields.Many2one("vendor.partial.payment.line")

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
        if sm_debit_move:
            if not sm_debit_move.invoice_id:
                if sm_debit_move.partial_pay_id:
                    amount_to_reconcile += sm_debit_move.partial_pay_id.amount_to_pay
                    amount_reconcile = amount_to_reconcile
                    sm_debit_move.partial_pay_id = False
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