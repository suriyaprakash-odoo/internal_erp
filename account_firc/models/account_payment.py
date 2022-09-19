from odoo import api, exceptions, fields, models, _

class CustomerMultiPayment(models.Model):
    _inherit = "customer.multi.payment"

    @api.multi
    def create_payments(self):
        res = super(CustomerMultiPayment, self).create_payments()
        if self.firc_no:
            firc_vals ={
                'name':self.firc_no,
                'move_id':self.account_move_id.id,
                'paid_amount':self.paid_amount,
                'paid_date': self.payment_date,
                'payment_ref':self.name,
            }
            firc_id = self.env["account.firc"].create(firc_vals)

            for line in self.credit_line_ids:
                if not line.invoice_id.firc_ids:
                    line.invoice_id.firc_ids = [(6, False, [firc_id.id])]
                else:
                    line.invoice_id.firc_ids = [(4, firc_id.id)]
            for line in self.debit_line_ids:
                if not line.invoice_id.firc_ids:
                    line.invoice_id.firc_ids = [(6, False, [firc_id.id])]
                else:
                    line.invoice_id.firc_ids = [(4, firc_id.id)]
        return res