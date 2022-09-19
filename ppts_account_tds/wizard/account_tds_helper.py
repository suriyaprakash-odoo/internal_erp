# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date

class AccountTdsRate(models.TransientModel):
    _name = 'tds.helper'
    _description = 'Account TDS Helper'
    
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id, readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner (Optional)')
    journal_id = fields.Many2one('account.journal','Payment Journal', required=True, default=lambda self: self.env.user.company_id.payment_journal_id, domain=[('type', '=', 'bank')])
    date = fields.Date('Deducted Till Date', required=True, default=date.today())
    tds_section_id = fields.Many2one('account.tds', 'Nature of Payment', required=True)
    
    @api.multi
    def create_payment(self):
        context = self.env.context
        payment_line = []; total = 0.0; bool = False
        if self.partner_id:
            tds_payment_ids = self.env['account.tds.payment'].search([('state','=','open'),('date','<=',self.date),('tds_section_id','=',self.tds_section_id.id),('company_id','=',self.company_id.id),('partner_id','=',self.partner_id.id)])
        else:
            tds_payment_ids = self.env['account.tds.payment'].search([('state','=','open'),('date','<=',self.date),('tds_section_id','=',self.tds_section_id.id),('company_id','=',self.company_id.id)])
        payment_id = self.env['tds.payment'].search([('id','=',context['active_id'])])
        for tds in tds_payment_ids:
            if tds.payment_id:
                if tds.payment_bal_amount > 0.0:
                    vals = {
                        'acc_payment_id' : tds.payment_id.id,
                        'name' : tds.name,
                        'partner_id': tds.partner_id.id,
                        'tds_payment_id': payment_id.id,
                        'acc_tds_payment_id': tds.id,
                        'account_id': tds.account_id.id,
                        'amount': tds.tds_amount,
                        'amount_unreconcile': tds.payment_bal_amount,
                        'amount_reconcile': tds.payment_bal_amount,
                        'payment_date': payment_id.payment_date,
                        }
                    total+=tds.payment_bal_amount
                    payment_line.append((0, 0, vals))
            if tds.invoice_id:
                if tds.bal_amount > 0.0:
                    vals = {
                        'invoice_id' : tds.invoice_id.id,
                        'name' : tds.name,
                        'partner_id': tds.partner_id.id,
                        'tds_payment_id': payment_id.id,
                        'acc_tds_payment_id': tds.id,
                        'account_id': tds.account_id.id,
                        'amount': tds.tds_amount,
                        'amount_unreconcile': tds.bal_amount,
                        'amount_reconcile': tds.bal_amount,
                        'payment_date': payment_id.payment_date,
                        }
                    total+=tds.bal_amount
                    payment_line.append((0, 0, vals))
        for line in payment_id.payment_line_ids:
            line.unlink()
        if len(payment_line) > 0:
            bool = True
        payment_id.write({
            'company_id': self.company_id.id,
            'journal_id': self.journal_id.id,
#             'amount': total,
            'payment_date': self.date,
            'payment_line_ids': payment_line,
            'is_payment_line' : bool
            })
        return True
    
    