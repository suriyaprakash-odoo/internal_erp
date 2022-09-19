from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class AccMultiPayment(models.Model):
    _name = "account.multi.payment"
    _order = 'name desc'
    _inherit = ['mail.thread']
    
    name = fields.Char("Name", default="Draft Receipt", track_visibility='always')
    partner_id = fields.Many2one('res.partner', string="Partner", domain=[('customer', '=', True)], required=True, track_visibility='always')
    paid_amount = fields.Float("Paid Amount", default=0.00, track_visibility='always')
    credit_amount = fields.Float("Credit Amount", compute='_compute_amount')
    journal_id = fields.Many2one("account.journal", string="Payment Journal", domain=[('type', 'in', ('bank', 'cash'))], track_visibility='always')
    payment_mode_id = fields.Many2one("ppts.payment.mode.master", string="Payment Mode", track_visibility='always')
    payment_date = fields.Date("Payment Date", default=lambda self: fields.Datetime.now(), track_visibility='always')
    communication = fields.Char("Memo", track_visibility='always')
    currency_id = fields.Many2one('res.currency', string="Currency", default=lambda self: self.env.user.company_id.currency_id, track_visibility='always')
    credit_line_ids = fields.One2many('account.multi.payment.line', 'multi_pay_id', string="Credit Line", domain=[('invoice_id.type', '=', 'out_invoice')])
    debit_line_ids = fields.One2many('account.multi.payment.line', 'multi_pay_id', string="Debit Line", domain=[('invoice_id.type', '=', 'out_refund')])
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
    firc_no = fields.Char(string='FIRC No.', size=15)
    payment_difference = fields.Monetary(string="Payment Difference", store=True, compute='_compute_amount', readonly=True, track_visibility='always')
    currency_rate = fields.Float('Currency Rate', track_visibility='always')
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
            val.credit_amount = credit - debit
            val.payment_difference = val.credit_amount - val.paid_amount
                        
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
                    'description': inv.number or False,
                    'amount_invoice': inv.amount_total or False,
                    'amount_residual': inv.residual or False,
                    'invoice_id': inv.id,
                    'invoice_date': inv.date_invoice or '',
                    'currency_id': inv.currency_id.id,
                }
                if inv.type == 'out_refund':
                    debit_lines.append((0, 0, line_vals))
                elif inv.type == 'out_invoice':
                    credit_lines.append((0, 0, line_vals))
            self.debit_line_ids = debit_lines
            self.credit_line_ids = credit_lines
            self.paid_amount = total_amount

    def get_all_payment_vals(self):
        # if self.credit_line_ids[0].currency_id.rate > 0.00:
#         if self.credit_line_ids[0].currency_rate > 0.00:
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
            'currency_rate': self.credit_line_ids[0].currency_rate,
            'payment_mode_id': self.payment_mode_id.id,
            'note': self.note,
            # 'payment_difference':self.payment_difference,
            # 'payment_difference_handling':self.payment_difference_handling,
            # 'writeoff_account_id':self.writeoff_account_id.id,
            # 'writeoff_label':self.writeoff_label
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
        if self.paid_amount > round(sum(line.amount_invoice for line in self.credit_line_ids), 4):
            raise UserError(_("Payment amount exceeds Invoice Amount"))

        if self.paid_amount == 0.0 and round(sum(line.amount_to_pay for line in self.credit_line_ids), 4) == 0.0:
            raise UserError(_("Please add some amount to process the invoices"))

        credit = sum(line.amount_to_pay for line in self.credit_line_ids)
        debit = sum(line.amount_to_pay for line in self.debit_line_ids)
        diff = self.credit_amount - self.paid_amount
        
        for line in self.credit_line_ids:
            if not line.amount_to_pay: 
                raise UserError(_(" Please add some amount to Credit lines"))
            
        if (self.credit_amount) != (self.paid_amount + diff):
            raise UserError(_("Payment amount exceeds Amount to pay"))

        for line in self.credit_line_ids:
            if line.amount_invoice < line.amount_to_pay:
                raise UserError(_("Amount to pay exceeds Invoice amount"))

        for line in self.debit_line_ids:
            if line.amount_invoice < line.amount_to_pay:
                raise UserError(_("Amount to pay exceeds Invoice amount"))

        if self.credit_line_ids or self.debit_line_ids:
            payment = self.env['account.payment'].create(self.get_all_payment_vals())
            payment.cus_multi_pay_id = self.id
            split_payment = []
            for i in self.credit_line_ids:
                if i.amount_to_pay != 0.0:
                    split_payment.append({i.invoice_id: -(i.amount_to_pay)})
            for i in self.debit_line_ids:
                if i.amount_to_pay != 0.0:
                    split_payment.append({i.invoice_id: (i.amount_to_pay)})
            if self.payment_difference:
                amount = list(split_payment[0].values())[0]
                val = amount + self.payment_difference
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
                inv_ids.firc_no = line.firc_no
        for line in self.debit_line_ids:
            inv_ids = self.env['account.invoice'].search([('id', '=', line.invoice_id.id)])
            if inv_ids:
                inv_ids.firc_no = line.firc_no
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


class AccPaymentLine(models.Model):
    _name = "account.multi.payment.line"

    description = fields.Char('Description')
    invoice_id = fields.Many2one('account.invoice', string="Invoice")
    amount_invoice = fields.Float('Amount Invoice')
    amount_residual = fields.Float('Residual')
    amount_invoice_dup = fields.Float(related='amount_invoice', string='Amount Invoice', store=True)
    amount_residual_dup = fields.Float(related='amount_residual', string='Residual', store=True)
    inverse_val = fields.Float('Inverse Value', digits=(12, 6))
    invoice_date = fields.Date('Invoice Date')
    amount_to_pay = fields.Float('Amount to pay', default=0.00)
    full_reconcile = fields.Boolean('Full Reconcile')
    currency_id = fields.Many2one('res.currency', string='Currency')
    firc_no = fields.Char(string='FIRC No.', size=15)
    multi_pay_id = fields.Many2one("account.multi.payment", "Payment ID")
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
        return super(AccPaymentLine, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('amount_invoice'):
            vals['amount_invoice'] = vals.get('amount_invoice')
        if vals.get('amount_residual'):
            vals['amount_residual'] = vals.get('amount_residual')
        return super(AccPaymentLine, self).write(vals)

class AccountMove(models.Model):
    _inherit = "account.payment"
    
    cus_multi_pay_id = fields.Many2one("account.multi.payment", "Payment ID")
    
    # multi customer invoice fully paid
    def _get_shared_move_line_vals_cus_inherit(self, debit, credit, amount_currency, move_id, invoice_id=False):
        return {
            'account_id': self.cus_multi_pay_id.writeoff_account_id.id,
            'partner_id': self.cus_multi_pay_id.partner_id.id,
            'name': self.cus_multi_pay_id.writeoff_label,
            'debit': debit,
            'credit': credit,
            'currency_id': self.currency_id.id,
            'amount_currency': amount_currency or False,
            'payment_id': self.id,
            'move_id': move_id
        }
        
