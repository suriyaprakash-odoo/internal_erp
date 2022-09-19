from odoo import api, exceptions, fields, models, _
from odoo.addons.test_new_api.models import Related
from odoo.addons import decimal_precision as dp
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
import math
import json
from datetime import date
from datetime import datetime
# from odoo.tools import amount_to_text_en, float_round

# from openerp import models, fields, api, _
# import openerp.addons.decimal_precision as dp
# from openerp.exceptions import UserError, ValidationError
# from datetime import date
# from openerp.tools import amount_to_text_en, float_round
# import math
# import json

MAP_INVOICE_TYPE_PARTNER_TYPE = {
    'out_invoice': 'customer',
    'out_refund': 'customer',
    'in_invoice': 'supplier',
    'in_refund': 'supplier',
}
# Since invoice amounts are unsigned, this is how we know if money comes in or goes out
MAP_INVOICE_TYPE_PAYMENT_SIGN = {
    'out_invoice': 1,
    'in_refund': 1,
    'in_invoice': -1,
    'out_refund': -1,
}

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'
    
    invoice_type = fields.Selection([('out_invoice', 'Invoice'), ('in_invoice', 'Vendor Bill'), ('out_refund', 'Refund'), ('in_refund', 'Vendor Refund')], string='Invoice Type')

    def update_invoice_ref(self, cr, uid, ids, context=None):
        cr.execute('UPDATE account_payment_line APL SET at_reference = AI.ats_invoice FROM account_invoice AI WHERE AI.number = APL.description; ')
        return True

class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"
    
    invoice_type = fields.Selection([('out_invoice', 'Invoice'), ('in_invoice', 'Vendor Bill'), ('out_refund', 'Refund'), ('in_refund', 'Vendor Refund')], string='Invoice Type')

class account_abstract_payment(models.AbstractModel):
    _inherit = ['account.abstract.payment']\
    
    @api.depends('amount', 'account_inv_adjustment_line.amount_to_pay', 'difference')
    def _compute_difference(self):
        for record in self:
            record.difference = record.amount - sum(line.amount_to_pay for line in record.account_inv_adjustment_line)


    account_inv_adjustment_line = fields.One2many('account.inv.adjustment.line', 'acc_inv_reg_id')
    type_of_payment= fields.Selection([('bulk_payment','All at once'),('split','Split')],'Type of Payment', required=True, default='bulk_payment')
    difference = fields.Float(compute='_compute_difference', string='Difference')
    payment_mode_id = fields.Many2one('ppts.payment.mode.master',string='Payment Mode')
    firc_no = fields.Char(string='FIRC No.',size=15)
    invoice_id = fields.Many2one('account.invoice',string='Invoice No')

class account_inv_adjustment_line(models.TransientModel):
    _name = 'account.inv.adjustment.line'

    @api.depends('amount_to_pay')       
    def compute_invoice_date(self):
        for order in self:
            if order.inv_id:
                inv_id = self.env['account.invoice'].search([('id','=',order.inv_id)])
                order.invoice_date = inv_id.date_invoice
    @api.depends('amount_to_pay')       
    def compute_residual(self):
        for order in self:
            if order.inv_id:
                inv_id = self.env['account.invoice'].search([('id','=',order.inv_id)])
                order.amount_residual = inv_id.residual
    @api.depends('amount_to_pay')       
    def compute_amount_invoice(self):
        for order in self:
            if order.inv_id:
                inv_id = self.env['account.invoice'].search([('id','=',order.inv_id)])
                order.amount_invoice = inv_id.amount_total
    @api.depends('amount_to_pay')       
    def compute_description(self):
        for order in self:
            if order.inv_id:
                inv_id = self.env['account.invoice'].search([('id','=',order.inv_id)])
                order.description = inv_id.number
    
    @api.depends('amount_to_pay')       
    def compute_invoice_acc(self):
        for order in self:
            if order.inv_id:
                inv_id = self.env['account.invoice'].search([('id','=',order.inv_id)])
                order.invoice_acc = inv_id.number

    acc_inv_reg_id = fields.Many2one('account.abstract.payment', 'account_inv_adjustment_line')
    description = fields.Char('Description',compute="compute_description", store=True)
    invoice_acc = fields.Char('Invoice',compute="compute_invoice_acc", store=True)
    amount_invoice = fields.Float('Amount Invoice',compute="compute_amount_invoice", store=True)
    amount_residual = fields.Float('Residual',compute="compute_residual", store=True)
    # dup_description = fields.Char('Description')
    # dup_invoice_acc = fields.Char('Invoice')
    # dup_amount_invoice = fields.Float('Amount Invoice')
    # dup_amount_residual = fields.Float('Residual')
    inverse_val = fields.Float('Inverse Value',digits=(12,6))
    currency_rate = fields.Float('Currency Rate')
    invoice_date = fields.Date('Invoice Date',compute="compute_invoice_date", store=True)
    amount_to_pay = fields.Float('Amount to pay',default=0.00)
    inv_id = fields.Char("Invoice ID")
    full_reconcile = fields.Boolean('Full Reconcile')
    currency_id = fields.Many2one('res.currency', string='Currency')
    firc_no = fields.Char(string='FIRC No.',size=15)

    @api.onchange('full_reconcile', 'amount_to_pay', 'amount_residual')
    def onchange_internal_type(self):
        if self.full_reconcile == True:
            self.amount_to_pay = self.amount_residual

    @api.onchange('amount_to_pay')
    def onchange_invoice_date(self):
        if self.inv_id:
            inv_id = self.env['account.invoice'].search([('id','=',self.inv_id)])
            self.invoice_date = inv_id.date_invoice

class account_register_payments(models.TransientModel):
    _name = "account.register.payments"
    _inherit = ['account.register.payments']
    _description = "Register payments on multiple invoices"

    # type_of_payment= fields.Selection([('bulk_payment','All at once'),('split','Split')],'Type of Payment', required=True, default='bulk_payment')
    # difference = fields.Float(compute='_compute_difference', string='Difference')
    check_number = fields.Integer(string="Check Number", copy=False, default=0,
        help="Number of the check corresponding to this payment. If your pre-printed check are not already numbered, "
             "you can manage the numbering in the journal configuration page.")
    
    def get_all_invoice_payment_vals(self):        
        if self.account_inv_adjustment_line[0].currency_id.rate > 0.00:
            amount_to_pay = self.amount / self.account_inv_adjustment_line[0].currency_id.rate
        else:
            amount_to_pay = self.amount
        # stop
        """ Hook for extension """
        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            # 'invoice_ids': [(4, inv.id, None) for inv in self._get_invoices()],
            # 'invoice_ids': [( 6, 0, self.invoice_ids)],
            'invoice_ids': [(6, 0, self.invoice_ids.ids)],
            'payment_type': self.payment_type,
            'amount': self.amount,
            # 'amount': amount_to_pay,
            # 'currency_id': self.currency_id.id,
            'currency_id': self.account_inv_adjustment_line[0].currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': self.partner_type,
            'check_no':self.check_number,
            'currency_rate':self.account_inv_adjustment_line[0].currency_rate,
            'payment_mode_id':self.payment_mode_id.id,

        }

    def get_invoicepayment_vals(self, invoice_line):
        
        if invoice_line.inverse_val > 0.00:
            amount_to_pay = invoice_line.amount_to_pay / invoice_line.inverse_val
        else:
            amount_to_pay = float(invoice_line.amount_to_pay)

        """ Hook for extension """
        # stop
        return {
            'journal_id': self.journal_id.id,
            'payment_method_id': self.payment_method_id.id,
            'payment_date': self.payment_date,
            'communication': self.communication,
            'invoice_ids': [(4, int(invoice_line.inv_id), None)],
            'payment_type': self.payment_type,
            'amount': float(invoice_line.amount_to_pay),
            # 'amount': amount_to_pay,
            # 'currency_id': self.currency_id.id,
            'currency_id': invoice_line.currency_id.id,
            'partner_id': self.partner_id.id,
            'partner_type': self.partner_type,
            'check_no':self.check_number,
            'currency_rate':invoice_line.currency_rate,
            'payment_mode_id':self.payment_mode_id.id,
        }
        
    @api.multi
    def create_payments(self):

        if self.amount > round(sum(line.amount_invoice for line in self.account_inv_adjustment_line),4):
            raise UserError(_("Payment amount exceeds Invoice Amount"))
        if self.amount > round(sum(line.amount_to_pay for line in self.account_inv_adjustment_line),4):
            raise UserError(_("Payment amount exceeds Amount to pay"))
        if self.amount < round(sum(line.amount_to_pay for line in self.account_inv_adjustment_line),4):
            raise UserError(_("Amount to pay exceeds Payment amount"))
        for line in self.account_inv_adjustment_line:
            if line.amount_invoice < line.amount_to_pay:
                raise UserError(_("Amount to pay exceeds Invoice amount"))
        
        if self.type_of_payment=='bulk_payment':
            payment = self.env['account.payment'].create(self.get_all_invoice_payment_vals())
            payment.post()
        else:
            for invoice_line in self.account_inv_adjustment_line:
                payment = self.env['account.payment'].create(self.get_invoicepayment_vals(invoice_line))
                payment.post()
        for line in self.account_inv_adjustment_line:
            inv_ids = self.env['account.invoice'].search([('id','=',line.inv_id)])
            if inv_ids:
                inv_ids.firc_no = line.firc_no
        return {'type': 'ir.actions.act_window_close'}

    
    @api.model
    def default_get(self, fields):
        rec = super(account_register_payments, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')

        values = []
        invoice_obj = self.env['account.invoice']
        invoice_ids = invoice_obj.search([('id', 'in' , active_ids)])
        for invoice_id in invoice_ids:
            invoice_id_brow = self.env['account.invoice'].browse(invoice_id)
            #raise UserError(_(invoice_id_brow.id.number))
            # aa = datetime.strptime(invoice_id_brow.id.date_invoice,'%Y-%m-%d')
            # aa = datetime.strftime(aa,'%Y-%m-%d')
            
            values.append((0, 0, {
                'inv_id' : invoice_id_brow.id.id,
                'description': invoice_id_brow.id.number,
                'invoice_acc': invoice_id_brow.id.number,
                'amount_invoice': invoice_id_brow.id.amount_total,
                'amount_residual': invoice_id_brow.id.residual,
                'currency_id': invoice_id_brow.id.currency_id.id,
            }))

        # Checks on context parameters
        if not active_model or not active_ids:
            raise UserError(
                _("Programmation error: wizard action executed without active_model or active_ids in context."))
        if active_model != 'account.invoice':
            raise UserError(_(
                "Programmation error: the expected model for this action is 'account.invoice'. The provided one is '%d'.") % active_model)

        # Checks on received invoice records
        invoices = self.env[active_model].browse(active_ids)
        if any(invoice.state != 'open' for invoice in invoices):
            raise UserError(_("You can only register payments for open invoices"))
        if any(inv.commercial_partner_id != invoices[0].commercial_partner_id for inv in invoices):
            raise UserError(
                _("In order to pay multiple invoices at once, they must belong to the same commercial partner."))
        if any(MAP_INVOICE_TYPE_PARTNER_TYPE[inv.type] != MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type] for inv in
               invoices):
            raise UserError(_("You cannot mix customer invoices and vendor bills in a single payment."))
        if any(inv.currency_id != invoices[0].currency_id for inv in invoices):
            raise UserError(_("In order to pay multiple invoices at once, they must use the same currency."))
        total_amount = sum(inv.residual * MAP_INVOICE_TYPE_PAYMENT_SIGN[inv.type] for inv in invoices)
        rec.update({
            'amount': abs(total_amount),
            'currency_id': invoices[0].currency_id.id,
            'payment_type': total_amount > 0 and 'inbound' or 'outbound',
            'partner_id': invoices[0].commercial_partner_id.id,
            'partner_type': MAP_INVOICE_TYPE_PARTNER_TYPE[invoices[0].type],
            'account_inv_adjustment_line': values
        })
        return rec

class account_move(models.Model):
    _inherit = "account.move"

    payment_mode_id = fields.Many2one('ppts.payment.mode.master',string='Payment Mode')

class account_move_line(models.Model):
    _inherit = "account.move.line"

    payment_mode_id = fields.Many2one(related='move_id.payment_mode_id', string="Payment Mode",store=True)

class account_payment(models.Model):
    _inherit = "account.payment"

    currency_rate = fields.Float('Currency Rate')
    payment_mode_id = fields.Many2one('ppts.payment.mode.master',string='Payment Mode')
    note = fields.Text(string='Note')

# _2017
#     da_shown
#     da_type
    @api.multi
    def show_debit_adjusted(self):
        adjustments=[]
        for line in self.account_invoice_amount_line:
            line.unlink()
        for line in self.invoice_ids:
            if line.move_id:
                for move_line in line.move_id.line_ids:
                    if move_line.credit >0:
                       partial_recon_ids=self.env['account.partial.reconcile'].search([('da_type', '=', 'in_invoice'),('da_shown', '=', 'no'),('credit_move_id', '=', move_line.id)])
                       for partial_recon_id in partial_recon_ids:
                            values={}
                            if not partial_recon_id.debit_move_id.payment_id:
                                values.update({'invoice_id': partial_recon_id.debit_move_id.invoice_id.id, 'move_line_id':partial_recon_id.debit_move_id.id, 'amount': partial_recon_id.debit_move_id.debit, 'date': partial_recon_id.debit_move_id.date})
                                adjustments.append((0, 0, values))
                                partial_recon_id.write({'da_shown':'yes'})
                    if move_line.debit >0:
                       partial_recon_ids=self.env['account.partial.reconcile'].search([('da_type', '=', 'out_invoice'),('da_shown', '=', 'no'),('debit_move_id', '=', move_line.id)])
                       for partial_recon_id in partial_recon_ids:
                            values={}
                            if not partial_recon_id.credit_move_id.payment_id:
                                values.update({'invoice_id': partial_recon_id.credit_move_id.invoice_id.id, 'move_line_id':partial_recon_id.credit_move_id.id, 'amount': partial_recon_id.credit_move_id.credit, 'date': partial_recon_id.credit_move_id.date})
                                adjustments.append((0, 0, values))
                                partial_recon_id.write({'da_shown':'yes'})

        self.account_invoice_amount_line = adjustments

    def _get_move_vals(self, journal=None):
        """ Return dict to create the payment move
        """
        journal = journal or self.journal_id
        if not journal.sequence_id:
            raise UserError(_('Configuration Error !'), _('The journal %s does not have a sequence, please specify one.') % journal.name)
        if not journal.sequence_id.active:
            raise UserError(_('Configuration Error !'), _('The sequence of journal %s is deactivated.') % journal.name)
        name = self.move_name or journal.with_context(ir_sequence_date=self.payment_date).sequence_id.next_by_id()
        return {
            'name': name,
            'date': self.payment_date,
            'ref': self.communication or '',
            'company_id': self.company_id.id,
            'journal_id': journal.id,
            'narration': self.note,
        }

#     @api.multi
#     def post(self):
#         """ Create the journal items for the payment and update the payment's state to 'posted'.
#             A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
#             and another in the destination reconciliable account (see _compute_destination_account_id).
#             If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
#             If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
#         """
#         for rec in self:
#             if rec.state != 'draft':
#                 raise UserError(
#                     _("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)
# 
#             if any(inv.state != 'open' for inv in rec.invoice_ids):
#                 raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
# 
#             # Use the right sequence to set the name
#             if rec.payment_type == 'transfer':
#                 sequence = rec.env.ref('account.sequence_payment_transfer')
#             else:
#                 if rec.partner_type == 'customer':
#                     if rec.payment_type == 'inbound':
#                         sequence = rec.env.ref('account.sequence_payment_customer_invoice')
#                     if rec.payment_type == 'outbound':
#                         sequence = rec.env.ref('account.sequence_payment_customer_refund')
#                 if rec.partner_type == 'supplier':
#                     if rec.payment_type == 'inbound':
#                         sequence = rec.env.ref('account.sequence_payment_supplier_refund')
#                     if rec.payment_type == 'outbound':
#                         sequence = rec.env.ref('account.sequence_payment_supplier_invoice')
#             rec.name = sequence.with_context(ir_sequence_date=rec.payment_date).next_by_id()
# 
#             # Create the journal entry
#             amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
#             rec.currency_rate = self.currency_rate
#             move = rec._create_payment_entry(amount)
# 
#             # In case of a transfer, the first journal entry created debited the source liquidity account and credited
#             # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
#             if rec.payment_type == 'transfer':
#                 transfer_credit_aml = move.line_ids.filtered(
#                     lambda r: r.account_id == rec.company_id.transfer_account_id)
#                 transfer_debit_aml = rec._create_transfer_entry(amount)
#                 (transfer_credit_aml + transfer_debit_aml).reconcile()
# 
#             rec.state = 'posted'
#             # PPTS customization for amount in words # Import math and amount in words library
#             # check_amount_in_wordss = amount_to_text_en.amount_to_text(math.floor(self.amount), lang='en', currency='')
#             # check_amount_in_wordss = check_amount_in_wordss.replace(' and Zero Cent', '')  # Ugh
#             # decimals = self.amount % 1
#             # if decimals >= 10 ** -2:
#             #     check_amount_in_wordss += _(' and %s/100') % str(
#             #         int(round(float_round(decimals * 100, precision_rounding=1))))
#             # self.check_amount_in_words = check_amount_in_wordss
# 
#             # rec.check_amount_in_words = self.check_amount_in_words
#             
#             
#             
#             
#             #raise UserError(_())
#             for rec_inv_id in rec.invoice_ids:
#                 #raise UserError(_(rec_inv_id.amount_total_signed))
#                 rec.account_payment_line.create({
#                     'pay_reg_id': rec.id,
#                     'date': rec_inv_id.date_invoice,
#                     'description': rec_inv_id.number,
#                     'vendor_ref': rec_inv_id.reference,
#                     'original_amt': rec_inv_id.amount_total,
#                     'amt_due': rec_inv_id.residual,
#                     'discount': 0.00,
#                     'amount': rec.amount,
#                     # 'at_reference': rec_inv_id.ats_invoice,
#                 })

#     def _create_payment_entry(self, amount):
#         """ Create a journal entry corresponding to a payment, if the payment references invoice(s) they are reconciled.
#             Return the journal entry.
#         """
#         aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
# 
#         move_vals = self._get_move_vals()
#         move_vals['payment_mode_id'] = self.payment_mode_id.id
#         
#         move = self.env['account.move'].create(move_vals)
#         if not self._context.get('split_payment'):
#             debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount,
#                                                                                                                              self.currency_id,
#                                                                                                                              self.company_id.currency_id)
# 
#             # raise UserError(_(move))
# 
#             # Write line corresponding to invoice payment
#             counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
#             counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
#             counterpart_aml_dict.update(
#                 {'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False})
#             if self.currency_rate:
#                 current_amt = self.currency_rate * counterpart_aml_dict['amount_currency']
#                 if current_amt < 0:
#                     current_amt = current_amt * -1
#                 counterpart_aml_dict.update({'credit': current_amt})
# 
#             #Round off Credit and debit amount by jana
#             journal_vals = self.env['account.journal'].search_read([('id','=',self.journal_id.id)],limit=1)[0]
#             if journal_vals.get('round_up', False):
#                 counterpart_aml_dict.update({'debit':round(counterpart_aml_dict.get('debit',0)),'credit':round(counterpart_aml_dict.get('credit',0))})
# 
#             counterpart_aml = aml_obj.create(counterpart_aml_dict)
#             # raise UserError(_("Here"))
#             # stop
#             # Reconcile with the invoices
#             if self.payment_difference_handling == 'reconcile':
#                 self.invoice_ids.register_payment(counterpart_aml, self.writeoff_account_id, self.journal_id)
#             else:
#                 self.invoice_ids.register_payment(counterpart_aml)
#             
#             # Write counterpart lines
#             liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
#             liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
#             if self.currency_rate:
#                 current_amt = self.currency_rate * counterpart_aml_dict['amount_currency']
#                 if current_amt < 0:
#                     current_amt = current_amt * -1
#                 liquidity_aml_dict.update({'debit': current_amt})
# 
#             #Round off Credit and debit amount by jana
#             if journal_vals.get('round_up', False):
#                 liquidity_aml_dict.update({'debit':round(liquidity_aml_dict.get('debit',0)),'credit':round(liquidity_aml_dict.get('credit',0))})
# 
#             aml_obj.create(liquidity_aml_dict)
#         elif self._context.get('split_payment'):
# 
#             for loop in self._context['split_payment']:
#                 invoice_ids = list(loop.keys())[0]
#                 loop_amount = list(loop.values())[0]
#                 debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(loop_amount,
#                                                                                                                                  self.currency_id,
#                                                                                                                                  self.company_id.currency_id)
# 
#                 # raise UserError(_(move))
# 
#                 # Write line corresponding to invoice payment
#                 counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
#                 counterpart_aml_dict.update(self._get_counterpart_move_line_vals(invoice_ids))
#                 counterpart_aml_dict.update(
#                     {'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False})
# 
#                 if self.currency_rate:
#                     current_amt = self.currency_rate * counterpart_aml_dict['amount_currency']
#                     if current_amt < 0:
#                         current_amt = current_amt * -1
#                     counterpart_aml_dict.update({'credit': current_amt})
# 
#                 #Round off Credit and debit amount by jana
#                 journal_vals = self.env['account.journal'].search_read([('id','=',self.journal_id.id)],limit=1)[0]
#                 if journal_vals.get('round_up', False):
#                     counterpart_aml_dict.update({'debit':round(counterpart_aml_dict.get('debit',0)),'credit':round(counterpart_aml_dict.get('credit',0))})
# 
#                 counterpart_aml = aml_obj.create(counterpart_aml_dict)
# 
#                 # raise UserError(_("Here"))
# 
#                 # Reconcile with the invoices
#                 if self.payment_difference_handling == 'reconcile':
#                     invoice_ids.register_payment(counterpart_aml, self.writeoff_account_id, self.journal_id)
#                 else:
#                     invoice_ids.register_payment(counterpart_aml)
# 
#             # Write counterpart lines
#             debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount,
#                                                                                                                              self.currency_id,
#                                                                                                                              self.company_id.currency_id)
#             liquidity_aml_dict = self._get_shared_move_line_vals(credit, debit, -amount_currency, move.id, False)
#             liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
#             if self.currency_rate:
#                 current_amt = self.currency_rate * counterpart_aml_dict['amount_currency']
#                 if current_amt < 0:
#                     current_amt = current_amt * -1
#                 liquidity_aml_dict.update({'debit': current_amt})
# 
#             #Round off Credit and debit amount by jana
#             if journal_vals.get('round_up', False):
#                 liquidity_aml_dict.update({'debit':round(liquidity_aml_dict.get('debit',0)),'credit':round(liquidity_aml_dict.get('credit',0))})
# 
#             aml_obj.create(liquidity_aml_dict)
#         move.post()
#         return move

    def _create_transfer_entry(self, amount):
        """ Create the journal entry corresponding to the 'incoming money' part of an internal transfer, return the reconciliable move line
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        debit, credit, amount_currency = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount,
                                                                                                            self.currency_id,
                                                                                                            self.company_id.currency_id)
        amount_currency = self.destination_journal_id.currency_id and self.currency_id.with_context(
            date=self.payment_date).compute(amount, self.destination_journal_id.currency_id) or 0

        dst_move = self.env['account.move'].create(self._get_move_vals(self.destination_journal_id))

        dst_liquidity_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, dst_move.id)
        dst_liquidity_aml_dict.update({
            'name': _('Transfer from %s') % self.journal_id.name,
            'account_id': self.destination_journal_id.default_credit_account_id.id,
            'currency_id': self.destination_journal_id.currency_id.id,
            'payment_id': self.id,
            'journal_id': self.destination_journal_id.id, })
        aml_obj.create(dst_liquidity_aml_dict)

        transfer_debit_aml_dict = self._get_shared_move_line_vals(credit, debit, 0, dst_move.id)
        transfer_debit_aml_dict.update({
            'name': self.name,
            'payment_id': self.id,
            'account_id': self.company_id.transfer_account_id.id,
            'journal_id': self.destination_journal_id.id})
        if self.currency_id != self.company_id.currency_id:
            transfer_debit_aml_dict.update({
                'currency_id': self.currency_id.id,
                'amount_currency': -self.amount,
            })
        transfer_debit_aml = aml_obj.create(transfer_debit_aml_dict)
        dst_move.post()
        return transfer_debit_aml

    account_payment_line = fields.One2many('account.payment.line', 'pay_reg_id')
    check_no = fields.Char('Check Number', store=True)
    account_invoice_amount_line = fields.One2many('account.invoice.amount.line', 'invoice_amount_id')

    
    @api.multi
    def print_checks(self):

        """ Check that the recordset is valid, set the payments state to sent and call print_checks() """
        # Since this method can be called via a client_action_multi, we need to make sure the received records are what we expect
        self = self.filtered(lambda r: r.payment_method_id.code == 'check_printing' and r.state != 'reconciled')

        if len(self) == 0:
            raise UserError(_("Payments to print as a checks must have 'Check' selected as payment method and "
                              "not have already been reconciled"))
        if any(payment.journal_id != self[0].journal_id for payment in self):
            raise UserError(_("In order to print multiple checks at once, they must belong to the same bank journal."))

        self.filtered(lambda r: r.state == 'draft').post()
        self.write({'state': 'sent'})

        if not self[0].journal_id.check_manual_sequencing:
            # The wizard asks for the number printed on the first pre-printed check
            # so payments are attributed the number of the check the'll be printed on.
            last_printed_check = self.search([
                ('journal_id', '=', self[0].journal_id.id),
                ('check_number', '!=', 0)], order="check_number desc", limit=1)
            next_check_number = last_printed_check and last_printed_check.check_number + 1 or 1
            return {
                'name': _('Print Pre-numbered Checks'),
                'type': 'ir.actions.act_window',
                'res_model': 'print.prenumbered.checks',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': {
                    'payment_ids': self.ids,
                    'default_next_check_number': next_check_number,
                }
            }
        else:
            # return self.do_print_checks()
            return self.env['report'].get_action(self, 'ppts_imporvements.report_check')

    @api.multi
    def unmark_sent(self):
        self.write({'state': 'posted'})

    @api.multi
    def do_print_checks(self):
        """ This method is a hook for l10n_xx_check_printing modules to implement actual check printing capabilities """
        raise UserError(
            _("There is no check layout configured.\nMake sure the proper check printing module is installed"
              " and its configuration (in company settings > 'Configuration' tab) is correct."))


class account_payment_line(models.Model):
    _name = 'account.payment.line'

    pay_reg_id = fields.Many2one('account.payment', 'account_inv_adjustment_line', ondelete='cascade', index=True, copy=False)
    date = fields.Date('Date')
    description = fields.Char('Reference')
    vendor_ref = fields.Char('Reference Number')
    original_amt = fields.Float('Orig. Amt', digits=dp.get_precision('Amount'), default=0.0)
    amt_due = fields.Float('Amt. Due', digits=dp.get_precision('Amount'), default=0.0)
    discount = fields.Float('Discount', digits=dp.get_precision('Amount'), default=0.0)
    amount = fields.Float('Amount', digits=dp.get_precision('Amount'), default=0.0)
    at_reference = fields.Char('AT Reference', store=True, copy=False)
    currency_id = fields.Many2one(related='pay_reg_id.currency_id', store=True, string='Currency', readonly=True)

# 03_07_2017  George
class account_invoice_amount_line(models.Model):
    _name = 'account.invoice.amount.line'

    invoice_amount_id = fields.Many2one('account.payment', 'account_inv_adjustment_line')
    invoice_id = fields.Many2one('account.invoice', 'Invoice Ref #')
    move_line_id = fields.Many2one('account.move.line', 'Move Ref #')
    amount = fields.Float('Amount', digits=dp.get_precision('Amount'), default=0.0)
    notes = fields.Char('Notes')
    date = fields.Date('Date')

    # 03_07_2017  George To be removed
    # @api.v7
    # def onchange_invoice_id(self,cr, uid, ids, invoice_id):
    #     val = {}
    #     if invoice_id:
    #         invoice = self.pool.get('account.invoice').browse(cr, uid, invoice_id)
    #         val = {'value':
    #             {
    #             'amount' : invoice.payments_widget,
    #             'date':  invoice.date_invoice
    #             }
    #             }
    #     return val



# class print_pre_numbered_checks(models.TransientModel):
#     _inherit = 'print.prenumbered.checks'

#     @api.multi
#     def print_checks(self):
#         check_number = self.next_check_number
#         payments = self.env['account.payment'].browse(self.env.context['payment_ids'])
#         for payment in payments:
#             payment.check_number = check_number
#             check_number += 1

#         return payments.do_print_checks()

    # 03_07_2017  George  In Payments, Adjusted / Amount Due is not showing up.
class AccountPartialReconcileCashBasis(models.Model):
    _inherit = 'account.partial.reconcile'

    da_type = fields.Char('Debit Adjustment')
    da_shown = fields.Selection([('yes','Yes'),('no','No')],'Debit Adjustment Shown', default='no')
