# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError

class AccounInvoiceupdate(models.TransientModel):
    """
    This wizard is used to change the e BRC no update
    """
    _name = 'e.brc.no.update'
    _description = 'Update e BRC No'

    from_date = fields.Date(string='From Date',default=datetime.today(),help='Select from Date.')
    to_date = fields.Date(string='To Date',default=datetime.today(),help='Select to Date.')
    state = fields.Selection([('open','Open'),('paid','Paid')], default="paid", string="Status")
    header_line_ids = fields.One2many('e.brc.update.line', 'line_id')
    
    @api.onchange('state','from_date','to_date')
    def onchange_status(self):
        if self.from_date and self.to_date:
            if self.from_date > self.to_date:
                raise UserError(_('From Date should be less than To Date'))
            if self.state:
                vals = []
                inv_ids = self.env['account.invoice'].search([('state','=',self.state),('date_invoice','>=',self.from_date),('date_invoice','<=',self.to_date)])
                if inv_ids:
                    for inv_rec in inv_ids:
                        vals.append({
                        'invoice_id': inv_rec.id,
                        'invoice_date': inv_rec.date_invoice,
                        'customer_id': inv_rec.partner_id.id,
                        'amount_total': inv_rec.amount_total,
                        'dup_invoice_id': inv_rec.id,
                        'dup_invoice_date': inv_rec.date_invoice,
                        'dup_customer_id': inv_rec.partner_id.id,
                        'dup_amount_total': inv_rec.amount_total,
                        
                        })
                self.update({'header_line_ids':vals})

    @api.multi
    def update_e_brc_no(self):
        if self.header_line_ids:
            for line in self.header_line_ids:
                if line.invoice_id.e_brc_no:
                    line.invoice_id.e_brc_no = line.invoice_id.e_brc_no + ' | ' + line.ebrc_no
                else:
                    line.invoice_id.e_brc_no = line.ebrc_no

class PrepareInvoiceLine(models.TransientModel):
    _name = "e.brc.update.line"

    line_id = fields.Many2one('e.brc.no.update', string="e BRC Invoice Line")
    invoice_id = fields.Many2one('account.invoice','Invoice No')
    invoice_date = fields.Date('Invoice Date')
    customer_id = fields.Many2one('res.partner','Customer Name')
    amount_total = fields.Char("Price")
    ebrc_no = fields.Char('e BRC No')
    dup_invoice_id = fields.Many2one('account.invoice','Invoice No')
    dup_invoice_date = fields.Date('Invoice Date')
    dup_customer_id = fields.Many2one('res.partner','Customer Name')
    dup_amount_total = fields.Char("Price")
