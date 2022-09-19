from odoo import api, fields, models, _
from odoo.exceptions import  UserError


class RegisterPayment(models.Model):
    _inherit = 'account.payment'

    firc_no = fields.Char("FIRC Number")

    @api.multi
    def action_validate_invoice_payment(self):
        res = super(RegisterPayment, self).action_validate_invoice_payment()
        if self.firc_no:
            for invoice in self.invoice_ids:
                firc_vals ={
                    'name':self.firc_no,
                    'move_id':invoice.move_id.id,
                    'paid_amount':self.amount,
                    'paid_date': self.payment_date,
                    'payment_ref':self.name,
                }
                firc_id = self.env["account.firc"].create(firc_vals)

                if not invoice.firc_ids:
                    invoice.firc_ids = [(6, False, [firc_id.id])]
                else:
                    invoice.firc_ids = [(4, firc_id.id)]
                if not invoice.firc_ids:
                    invoice.firc_ids = [(6, False, [firc_id.id])]
                else:
                    invoice.firc_ids = [(4, firc_id.id)]
        return res


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.register.payments'

    firc_no = fields.Char("FIRC Number")

    @api.multi
    def create_payments(self):
        ctx = self._context.copy()
        if self.amount > round(sum(line.amount_invoice for line in self.account_inv_adjustment_line), 4):
            raise UserError(_("Payment amount exceeds Invoice Amount"))
        if self.amount > round(sum(line.amount_to_pay for line in self.account_inv_adjustment_line), 4):
            raise UserError(_("Payment amount exceeds Amount to pay"))
        if self.amount < round(sum(line.amount_to_pay for line in self.account_inv_adjustment_line), 4):
            raise UserError(_("Amount to pay exceeds Payment amount"))
        for line in self.account_inv_adjustment_line:
            if line.amount_invoice < line.amount_to_pay:
                raise UserError(_("Amount to pay exceeds Invoice amount"))
        payment = False
        if self.type_of_payment == 'bulk_payment':
            payment = self.env['account.payment'].create(self.get_all_invoice_payment_vals())
            split_payment = []
            for i in self.account_inv_adjustment_line:
                if i.amount_to_pay != 0.0:
                    inv_id = self.env['account.invoice'].search([('number','=',i.invoice_acc)])
                    split_payment.append({inv_id: -(i.amount_to_pay)})
            ctx.update({'split_payment': split_payment})
            payment.with_context(ctx).post()
        else:
            split_payment = []
            for invoice_line in self.account_inv_adjustment_line:
                payment = self.env['account.payment'].create(self.get_invoicepayment_vals(invoice_line))
                if invoice_line.amount_to_pay != 0.0:
                    inv_id = self.env['account.invoice'].search([('number','=',invoice_line.invoice_acc)])
                    split_payment.append({inv_id: -(invoice_line.amount_to_pay)})
            ctx.update({'split_payment': split_payment})
            payment.with_context(ctx).post()

        if self.firc_no:
            if payment:
                move_line_id = self.env["account.move.line"].search([('payment_id','=',payment.id)])[0]
                if move_line_id:
                    move_id = move_line_id.move_id.id
                firc_vals = {
                    'name': self.firc_no,
                    'move_id': move_id,
                    'paid_amount': self.amount,
                    'paid_date': self.payment_date,
                    'payment_ref': payment.name,
                }
                firc_id = self.env["account.firc"].create(firc_vals)
                for line in self.account_inv_adjustment_line:
                    inv_id = self.env['account.invoice'].search([('id', '=', line.inv_id)])[0]
                    if inv_id:
                        if not inv_id.firc_ids:
                            inv_id.firc_ids = [(6, False, [firc_id.id])]
                        else:
                            inv_id.firc_ids = [(4, firc_id.id)]
                        if not inv_id.firc_ids:
                            inv_id.firc_ids = [(6, False, [firc_id.id])]
                        else:
                            inv_id.firc_ids = [(4, firc_id.id)]

        return {'type': 'ir.actions.act_window_close'}