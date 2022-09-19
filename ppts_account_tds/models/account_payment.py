from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
           
class AccountPayment(models.Model):
    _inherit = "account.payment"
    
    is_apply = fields.Boolean('Apply TDS ?', copy=False, track_visibility='onchange')
    tds_section_id = fields.Many2one('account.tds',"TDS Section", copy=False, track_visibility='onchange')
    amount_payment = fields.Monetary('Payment Amount', readonly=True, copy=False)
    amount_tds = fields.Monetary('TDS Amount', store=True, compute='_compute_tds_amount', readonly=True, copy=False, track_visibility='onchange')
    amount_total = fields.Monetary('Payment Amount', store=True, compute='_compute_tds_amount', readonly=True, copy=False)
    tds_payment_ids = fields.One2many('account.tds.payment','payment_id')
    is_gen = fields.Boolean('Gen', default=False, copy=False)
    domain_section_id = fields.Many2one('account.tds', related="partner_id.tds_section_id")
    without_pan = fields.Boolean('Process Without PAN', track_visibility='always')
    
    @api.onchange('is_apply','partner_id','amount_payment')
    def onchange_tds_partner_id(self):
        self.amount_payment = self.amount
        if self.is_apply:
            self.tds_section_id = self.partner_id.tds_section_id.id
        else:
            self.is_gen = False
            self.tds_section_id = False
        
    @api.depends('tds_payment_ids.amount')
    def _compute_tds_amount(self):
        for val in self:
            val.amount_payment = val.amount
            amt_total = 0.00
            for line in val.tds_payment_ids:
                amt_total += line.tds_amount
            val.amount_tds = amt_total
            val.amount_total = val.amount - amt_total
    
    @api.multi
    def gen_tds(self):
        self.amount_payment = self.amount
        if self.amount <= 0:
            raise UserError(_("Enter Valid Payment Amount."))
        if self.is_apply:
            tds = sur = tax = 0.00
            tds = self.amount*(self.tds_section_id.tds_percentage/100)
            sur = self.amount*(self.tds_section_id.sur_percentage/100)
            tax = tds+sur
            tds_payment_id = self.env['account.tds.payment'].search([('payment_id','=',self.id)])
            if tds_payment_id:
                tds_payment_id.write({
                    'payment_id': self.id,
                    'date': date.today(),
                    'code': self.tds_section_id.code,
                    'tds_deduct': self.is_apply,
                    'partner_id': self.partner_id.id,
                    'tds_section_id': self.tds_section_id.id,
                    'account_id': self.tds_section_id.account_id.id,
                    'amount': self.amount,
                    'tds_amount': tax,
                    'tds_amount_residual': tax,
                    'bal_amount': tax,
                    'payment_bal_amount': tax,
                    'tds_payable': self.amount-tax,
                    'state': 'draft',
                })
                tds_payment_line_id = self.env['account.tds.payment.line'].search([('payment_line_id','=',tds_payment_id.id)])
                if tds_payment_line_id:
                    tds_payment_line_id.write({
                            'payment_line_id': tds_payment_id.id,
                            'tax_type': 'tds',
                            'credit': tds,
                            'debit': 0,
                            'rate': self.tds_section_id.tds_percentage,
                            'base': tds_payment_id.amount})
                    tds_payment_line_id.write({
                        'payment_line_id': tds_payment_id.id,
                        'tax_type': 'sur',
                        'credit': sur,
                        'debit': 0,
                        'rate': self.tds_section_id.sur_percentage,
                        'base': tds_payment_id.amount,
                    })
                self.is_gen = True
            else:
                tds_payment_id = self.env['account.tds.payment'].create({
                    'payment_id': self.id,
                    'date': date.today(),
                    'code': self.tds_section_id.code,
                    'tds_deduct': self.is_apply,
                    'partner_id': self.partner_id.id,
                    'tds_section_id': self.tds_section_id.id,
                    'account_id': self.tds_section_id.account_id.id,
                    'amount': self.amount,
                    'tds_amount': tax,
                    'tds_amount_residual': tax,
                    'bal_amount': tax,
                    'payment_bal_amount': tax,
                    'tds_payable': self.amount-tax,
                    'state': 'draft',
                })
                if tds_payment_id:
                    tds_payment_line_id = self.env['account.tds.payment.line']
                    tds_payment_line_id.create({
                        'payment_line_id': tds_payment_id.id,
                        'tax_type': 'tds',
                        'credit': tds,
                        'debit': 0,
                        'rate': self.tds_section_id.tds_percentage,
                        'base': tds_payment_id.amount})
                    tds_payment_line_id.create({
                        'payment_line_id': tds_payment_id.id,
                        'tax_type': 'sur',
                        'credit': sur,
                        'debit': 0,
                        'rate': self.tds_section_id.sur_percentage,
                        'base': tds_payment_id.amount,
                    })
                self.is_gen = True
        
    @api.multi
    def post(self):
        if self.partner_id.tds_deductee_id.pan_check and self.partner_id.supplier:
            if not self.partner_id.pan_no:
                if self.without_pan == False:
                    raise UserError(_("No PAN is available for the selected partner.\n Contact your Manager/administrator!!!"))
        if self.is_gen:
            for rec in self:
                if rec.state != 'draft':
                    raise UserError(_("Only a draft payment can be posted."))
                if any(inv.state != 'open' for inv in rec.invoice_ids):
                    raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
                if rec.payment_type == 'transfer':
                    sequence_code = 'account.payment.transfer'
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.customer.invoice'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.customer.refund'
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence_code = 'account.payment.supplier.refund'
                        if rec.payment_type == 'outbound':
                            sequence_code = 'account.payment.supplier.invoice'
                rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
                if not rec.name and rec.payment_type != 'transfer':
                    raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))
                amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                move = rec._create_payment_entry_inherit(amount,self.amount_tds,self.amount_total)
                if rec.payment_type == 'transfer':
                    transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                    transfer_debit_aml = rec._create_transfer_entry(amount)
                    (transfer_credit_aml + transfer_debit_aml).reconcile()
                rec.write({'state': 'posted', 'move_name': move.name})
                tds_payment_ids = self.env['account.tds.payment'].search([('payment_id','=',self.id)])
                for pay in tds_payment_ids:
                    pay.write({
                    'name': move.name,
                    'state': 'open'
                    })
            return True
        else:
            for rec in self:
                if rec.state != 'draft':
                    raise UserError(
                        _("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)
                if any(inv.state != 'open' for inv in rec.invoice_ids):
                    raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
                if rec.payment_type == 'transfer':
                    sequence = rec.env.ref('account.sequence_payment_transfer')
                else:
                    if rec.partner_type == 'customer':
                        if rec.payment_type == 'inbound':
                            sequence = rec.env.ref('account.sequence_payment_customer_invoice')
                        if rec.payment_type == 'outbound':
                            sequence = rec.env.ref('account.sequence_payment_customer_refund')
                    if rec.partner_type == 'supplier':
                        if rec.payment_type == 'inbound':
                            sequence = rec.env.ref('account.sequence_payment_supplier_refund')
                        if rec.payment_type == 'outbound':
                            sequence = rec.env.ref('account.sequence_payment_supplier_invoice')
                rec.name = sequence.with_context(ir_sequence_date=rec.payment_date).next_by_id()
                amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
                rec.currency_rate = self.currency_rate
                move = rec._create_payment_entry(amount)
                if rec.payment_type == 'transfer':
                    transfer_credit_aml = move.line_ids.filtered(
                        lambda r: r.account_id == rec.company_id.transfer_account_id)
                    transfer_debit_aml = rec._create_transfer_entry(amount)
                    (transfer_credit_aml + transfer_debit_aml).reconcile()
                rec.state = 'posted'
                for rec_inv_id in rec.invoice_ids:
                    rec.account_payment_line.create({
                        'pay_reg_id': rec.id,
                        'date': rec_inv_id.date_invoice,
                        'description': rec_inv_id.number,
                        'vendor_ref': rec_inv_id.reference,
                        'original_amt': rec_inv_id.amount_total,
                        'amt_due': rec_inv_id.residual,
                        'discount': 0.00,
                        'amount': rec.amount,
                    })
    
    @api.multi
    def cancel(self):
        for line in self.tds_payment_ids:
            if line.tds_amount!=line.bal_amount:
                raise UserError(_('You cannot cancel the payment entry since TDS been already reconciled with vendor bills.'))
            else:
                line.unlink()
        return super(AccountPayment, self).cancel()
                
    def _create_payment_entry_inherit(self, amount, tds_amount, total_amount):
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)
        move = self.env['account.move'].create(self._get_move_vals())
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
            if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                amount_wo = total_payment_company_signed - total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            if amount_wo > 0:
                debit_wo = amount_wo
                credit_wo = 0.0
                amount_currency_wo = abs(amount_currency_wo)
            else:
                debit_wo = 0.0
                credit_wo = -amount_wo
                amount_currency_wo = -abs(amount_currency_wo)
            writeoff_line['name'] = self.writeoff_label
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit'] or (writeoff_line['credit'] and not counterpart_aml['credit']):
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit'] or (writeoff_line['debit'] and not counterpart_aml['debit']):
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo
        if not self.currency_id.is_zero(self.amount):
            if not self.currency_id != self.company_id.currency_id:
                amount_currency = 0
            if tds_amount:
                tds_amount, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(tds_amount, self.currency_id, self.company_id.currency_id, invoice_currency)
                liquidity_aml_dict = self._get_shared_move_line_vals(credit, tds_amount, -amount_currency, move.id, False)
                liquidity_aml_dict.update(self._get_liquidity_move_line_vals_tds(-amount))
                aml_obj.create(liquidity_aml_dict)
            if total_amount:
                total_amount, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(total_amount, self.currency_id, self.company_id.currency_id, invoice_currency)
                liquidity_aml_dict = self._get_shared_move_line_vals(credit, total_amount, -amount_currency, move.id, False)
                liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
                aml_obj.create(liquidity_aml_dict)
        move.post()
        self.invoice_ids.register_payment(counterpart_aml)
        return move
    
    def _get_liquidity_move_line_vals_tds(self, amount):
        name = self.name
        if self.payment_type == 'transfer':
            name = _('Transfer to %s') % self.destination_journal_id.name
        vals = {
            'name': name,
            'account_id': self.tds_section_id.account_id.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
        }
        if self.journal_id.currency_id and self.currency_id != self.journal_id.currency_id:
            amount = self.currency_id.with_context(date=self.payment_date).compute(amount, self.journal_id.currency_id)
            debit, credit, amount_currency, dummy = self.env['account.move.line'].with_context(date=self.payment_date).compute_amount_fields(amount, self.journal_id.currency_id, self.company_id.currency_id)
            vals.update({
                'amount_currency': amount_currency,
                'currency_id': self.journal_id.currency_id.id,
            })
        return vals
      