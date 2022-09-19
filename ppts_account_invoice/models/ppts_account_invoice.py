from odoo import api, exceptions, fields, models, _
from odoo.addons.test_new_api.models import Related
from docutils.nodes import field
from num2words import num2words
from odoo.exceptions import UserError, AccessError, ValidationError

import smtplib

class AccountInvoice(models.Model):

    _inherit = "account.invoice"
    
    #     default to custom template changed
    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env.ref('ppts_account_invoice.account_invoices_ppts').report_action(self)
    
    # @api.one
    # @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'tax_line_ids.amount_rounding',
    #              'currency_id', 'company_id', 'date_invoice', 'type','freight','inr_conversion','invoice_line_ids.quantity')
    # def _compute_amount(self):
    #     round_curr = self.currency_id.round
    #     self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
    #     self.amount_tax = sum(round_curr(line.amount_total) for line in self.tax_line_ids)
    #     self.amount_total = self.amount_untaxed + self.amount_tax
    #     amount_total_company_signed = self.amount_total
    #     amount_untaxed_signed = self.amount_untaxed
    #     if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
    #         currency_id = self.currency_id.with_context(date=self.date_invoice)
    #         amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
    #         amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
    #     sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
    #     self.amount_total_company_signed = amount_total_company_signed * sign
    #     self.amount_total_signed = self.amount_total * sign
    #     self.amount_untaxed_signed = amount_untaxed_signed * sign
    #     if self.segment == 'exp':
    #         self.insurance_value = round((self.amount_untaxed / 100.00) * 110  * (0.06 / 100.00))
    #         self.fob_value = round(self.amount_untaxed - self.insurance_value - self.freight,2)
    #         self.invoice_inr_value = round(self.amount_untaxed * self.inr_conversion)
    #         self.fob_inr_value = round(self.fob_value * self.inr_conversion)
    #         self.insurance_inr_value = round(self.insurance_value * self.inr_conversion)
    #         self.freight_inr_value = round(self.freight * self.inr_conversion)
    #     else:
    #         self.insurance_value = 0
    #         self.fob_value = 0.00
    #         self.invoice_inr_value = 0
    #         self.fob_inr_value = 0
    #         self.insurance_inr_value = 0
    #         self.freight_inr_value = 0


    @api.depends('amount_total','amount_untaxed')       
    def compute_amount_total_words(self):
        for order in self:
            if order.currency_id.name == 'INR':
                self._cr.execute(''' SELECT f_amount_to_words('%s','%s') '''%(order.amount_total,order.company_id.id))
                rows = self._cr.dictfetchall()
                order.amount_in_word = rows[0]['f_amount_to_words']
                order.amount_in_word = order.amount_in_word.replace(',','')
            else:
                order.amount_in_word = order.currency_id.amount_to_text(order.amount_total)
                order.amount_in_word = str(order.amount_in_word) + ' only'
                order.amount_in_word = order.amount_in_word.replace(',','')
            
    @api.depends('amount_total','amount_untaxed','currency_id')       
    def compute_currency_name(self):
        for order in self:
            if order.currency_id:
                order.currency_name = order.currency_id.name
            else:
                order.currency_name = ''

    firc_no = fields.Char(string="FIRC No.",size=15)
    softex_no = fields.Char(string="Softex No.",size=15)
    nsdl_ref_no = fields.Char(string="NSDL Reference No.",size=15)
    other_ref = fields.Char(string="Other Reference",size=15)
    e_brc_no = fields.Char(string="e.BRC No.",size=15)
    nsdl_ref_date = fields.Date(string="Dated")
    softex_ref_date = fields.Date(string="Dated")
    buyer_ref = fields.Char(string="Buyer's Order Reference",size=15,readonly=True, states={'draft': [('readonly', False)]})
    buyer_po_date = fields.Date(string="Buyer's Order Date",readonly=True, states={'draft': [('readonly', False)]})
    amount_in_word = fields.Char("Total (In Words)", compute="compute_amount_total_words", store=True)
    bank_id = fields.Many2one('res.bank','Bank',readonly=True, states={'draft': [('readonly', False)]})
    acc_number = fields.Many2one('res.partner.bank','Account Number',domain="[('bank_id','=',bank_id)]",readonly=True, states={'draft': [('readonly', False)]})
    bank_details = fields.Html(string="Bank Details",readonly=True, states={'draft': [('readonly', False)]})
    currency_name = fields.Char("Currency", compute="compute_currency_name", store=True)
    vendor_invoice = fields.Char("Vendor Invoice")

    # @api.one
    # def send_mail_test(self):
    #     for rec in self:
    #         receivers_email = 'thangaraj.murugesan@pptservices.com'

    #         server = smtplib.SMTP('mail.pptservices.com', 465)
            
    #         server.ssl()
    #         server.login("odootest@pptservices.com", "Odoo@123")
            
    #         message = 'Test mail'
    #         server.sendmail("odootest@pptservices.com", receivers_email, message)

    #         server.quit()
    #     return True

    # port_of_loading = fields.Char(string="Port of Loading",readonly=True, states={'draft': [('readonly', False)]})
    # place_of_acceptance = fields.Char(string="Place of Acceptance",readonly=True, states={'draft': [('readonly', False)]})
    # terms_delivery_payment = fields.Char(string="Terms & Delivery of Payment",readonly=True, states={'draft': [('readonly', False)]})
    # marks_container_no = fields.Char(string="Marks & Nos./Container No.",readonly=True, states={'draft': [('readonly', False)]})
    # description = fields.Char(string="Description of Goods / H.S.CODE NO.",readonly=True, states={'draft': [('readonly', False)]})
    # description_of_packages = fields.Char(string="Description of Packages",readonly=True, states={'draft': [('readonly', False)]})
    # no_kids_packages = fields.Char(string="No. & Kind Of Packages :",readonly=True, states={'draft': [('readonly', False)]})
    # lc_no = fields.Char(string="LC no :",readonly=True, states={'draft': [('readonly', False)]})
    # country_orgin = fields.Many2one("res.country", string="Country Orgin of goods",readonly=True, states={'draft': [('readonly', False)]})
    # country_final_dest = fields.Many2one("res.country", string="Country of final desitnation")
    # dispatch_id = fields.Many2one("nf.mode.of.dispatch", string="Mode of Dispatch",readonly=True, states={'draft': [('readonly', False)]})
    # declaration = fields.Html(string="Declaration",readonly=True, states={'draft': [('readonly', False)]})
    # freight = fields.Integer(string="Freight", readonly=True, states={'draft': [('readonly', False)]},track_visibility='always')
    # inr_conversion = fields.Float(string="Exchange Rate",readonly=True, states={'draft': [('readonly', False)]},track_visibility='always')
    # lut_no = fields.Char(string="LUT No",related="company_id.lut_no",readonly=True, states={'draft': [('readonly', False)]})
    # print_option = fields.Selection([('customer', 'Customer'),('fob', 'FOB'),('inr', 'FOB-INR'),('lut', 'LUT')],string="Print Type")
    # hsn_no = fields.Char("HSN No", readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]})
    # vehicle_no = fields.Char("Vehicle No", readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]})
    # date_of_supply = fields.Date("Date of Supply", readonly=True, states={'draft': [('readonly', False)],'open': [('readonly', False)]})
    # segment = fields.Selection(related='partner_id.segment', string="Segment", readonly=True,store=True)
    # tax_id = fields.Many2one('account.tax',compute='_get_so_id',string="Tax",readonly=True)
    # insurance_value = fields.Integer(string='Insurance Value', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    # fob_value = fields.Float(string='FOB Value', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    # invoice_inr_value = fields.Integer(string='Invoice Value', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    # insurance_inr_value = fields.Integer(string='Insurance Value', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    # freight_inr_value = fields.Integer(string='Freight Value', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    # fob_inr_value = fields.Integer(string='FOB Value', store=True, readonly=True, compute='_compute_amount', track_visibility='always')
    # so_id = fields.Many2one('sale.order',compute='_get_so_id', store=True, string="SO No.",readonly=True)
    # crates_no = fields.Char('Crates No')
    
    # @api.constrains('currency_id')
    # def _check_currency_validation(self):
    #     for rec in self:
    #         if rec.journal_id.currency_id.id != rec.currency_id.id and rec.journal_id.company_id.currency_id.id != rec.currency_id.id:
    #             raise ValidationError(_('Invoice Currency should be map Journal Currency'))
    #     return True

    @api.onchange('bank_id')
    def onchange_acc_number(self):
        self.acc_number = False

    @api.model
    def create(self, vals):
        journals = self.env['account.journal'].search([('id','=',vals.get('journal_id'))])
        res=super(AccountInvoice, self).create(vals)
        if res.partner_id.customer:
            res.journal_id.currency_id=vals.get('currency_id')
        return res

    @api.multi
    def write(self, vals):
        for line in self:
            if line.partner_id.customer:
                for journal in line.journal_id:
                    journal.currency_id = vals.get('currency_id')
        return super(AccountInvoice, self).write(vals)

    @api.onchange('acc_number')
    def onchange_bank_details(self):
        if self.acc_number:
            # details = 'Account Name : ' + str(self.acc_number.acc_name) +'<br> Bank : ' + str(self.bank_id.name) + '<br> Branch : ' + str(self.bank_id.branch) + '<br> Bank Address : ' + str(self.bank_id.street) + str(self.bank_id.street2) + '<br> ' + str(self.bank_id.city) + '<br> ' + str(self.bank_id.state.name) + '<br> ' + str(self.bank_id.country.name) + '-' + str(self.bank_id.zip) + '<br> Bank Contact : ' + str(self.bank_id.bank_contact) + '<br> Account Number : ' + str(self.acc_number.acc_number) + '<br> IFSCode : ' + str(self.bank_id.ifsc) + '<br> MICR Code : ' + str(self.bank_id.micr) + '<br> Branch Code : ' + str(self.bank_id.bic) + '<br> Swift Code : ' + str(self.bank_id.swift_code)
            
            acc_number,bank_name,branch_name,bank_add,bank_contact,a_acc_number,ifsc,micr,branch_code,swift_code = '','','','','','','','','',''
            details = """
            
            <p><strong>Bank Details:</strong></p>
            <table style='width:100%;background:transparent;'>
            <tbody>
            <tr style='background-color: white;background:transparent !important;'>
            <td style='width:15%;'>Account Name</td>
            <td >""" + str(self.acc_number.acc_name or '') + """</td>
            </tr>

            """
            if self.bank_id.name:
                bank_name = ''' ''' + """
                <tr style='background-color: white;background:transparent !important;'>
                <td >Bank</td>
                <td >""" + str(self.bank_id.name or '') + """</td>
                </tr>
                """
            else:
                bank_name = bank_name

            if self.bank_id.branch:
                branch_name = ''' ''' + """
                <tr style='background-color: white;background:transparent !important;'>
                <td >Branch</td>
                <td >""" +str(self.bank_id.branch or '') + """</td>
                </tr>
                """
            else:
                branch_name = branch_name

            if self.bank_id.street or self.bank_id.street2 or self.bank_id.city or self.bank_id.state.name or self.bank_id.country.name or self.bank_id.zip: 
                bank_add = """
                <tr style='background-color: white;background:transparent !important;'>
                <td >Bank Address</td>
                <td >""" + str(self.bank_id.street or '') + ' ' + str(self.bank_id.street2 or '') + ' ' + str(self.bank_id.city or '') + ' ' + str(self.bank_id.state.name or '') + ' ' + str(self.bank_id.country.name or '') + ' ' + str(self.bank_id.zip or '') + """</td>
                </tr>
                """
            else:
                bank_add = bank_add

            if self.bank_id.bank_contact:
                bank_contact = ''' ''' + """
                <tr style='background-color: white;background:transparent !important;'>
                <td >Bank Contact</td>
                <td >""" +str(self.bank_id.bank_contact or '') + """</td>
                </tr>
                """
            else:
                bank_contact = bank_contact

            if self.acc_number.acc_number:
                a_acc_number = ''' ''' + """
                <tr style='background-color: white;background:transparent !important;'>
                <td >Account Number</td>
                <td >""" +str(self.acc_number.acc_number or '') + """</td>
                </tr>
                """
            else:
                a_acc_number = a_acc_number

            if self.bank_id.ifsc:
                ifsc = ''' ''' + """
                <tr style='background-color: white;background:transparent !important;'>
                <td >IFSCode</td>
                <td >""" +str(self.bank_id.ifsc or '') + """</td>
                </tr>
                """
            else:
                ifsc = ifsc

            if self.bank_id.micr:
                micr = ''' ''' + """
                <tr style='background-color: white;background:transparent !important;'>
                <td >MICR Code</td>
                <td >""" +str(self.bank_id.micr or '') + """</td>
                </tr>
                """
            else:
                micr = micr

            if self.bank_id.branch_code:
                branch_code = ''' ''' + """
                <tr style='background-color: white;background:transparent !important;'>
                <td >Branch Code</td>
                <td >""" +str(self.bank_id.branch_code or '') + """</td>
                </tr>
                """
            else:
                branch_code = branch_code

            if self.bank_id.swift_code:
                swift_code = ''' ''' + """
                <tr style='background-color: white;background:transparent !important;'>
                <td >Swift Code</td>
                <td >""" +str(self.bank_id.swift_code or '') + """</td>
                </tr>
                """
            else:
                swift_code = swift_code

            t_close= """
                </tbody>
                </table>"""
            
            bank_details = details + bank_name + branch_name + bank_add + bank_contact + a_acc_number + ifsc + micr + branch_code + swift_code + t_close
            self.bank_details = bank_details
        else:    
            self.bank_details = ''
        
    # def get_subtotal(self,):
    #     amount_total = 0.00
    #     for record in self.invoice_line_ids:
    #         if record.is_package == False and record.is_transport == False:
    #             amount_total +=record.price_subtotal
    #     return amount_total
            
    # @api.multi
    # def _get_gst_tax_amount(self,name):
    #     val = 0
    #     for tax_id in self.tax_line_ids:
    #         #tax_name = l[0]
    #         if name in tax_id.name:
    #             val = tax_id.amount_total
    #             break
    #     return val

class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    project_code = fields.Char(string='Project Code',size=6)
    # gst_code = fields.Char(string='GST Code')
    gst_code_id = fields.Many2one('ppts.gst.code.master', string='GST Code')

class Bank(models.Model):

    _inherit = "res.bank"

    branch = fields.Char(string='Branch')
    branch_code = fields.Char(string='Branch Code')
    bank_contact = fields.Char(string='Bank Contact')
    ifsc = fields.Char(string='IFSCode')
    micr = fields.Char(string='MICR Code')
    swift_code = fields.Char(string='Swift Code')

class ResPartnerBank(models.Model):

    _inherit = "res.partner.bank"

    acc_name = fields.Char(string='Account Name')

class Country(models.Model):

    _inherit = "res.country"

    sez_code = fields.Char(string='Country Code as per SEZ Online ref.')
    
class AccountTax(models.Model):
    _inherit = "account.tax"
 
    type_tax_use = fields.Selection([('all','All'),('sale', 'Sales'), ('purchase', 'Purchases'), ('none', 'None')], 
        string='Tax Scope', required=True, default="all",
        help="Determines where the tax is selectable. Note : 'None' means a tax can't be used by itself, however it can still be used in a group.")
    
class ProductTemplate(models.Model):
    _inherit = "product.template"

    taxes_id = fields.Many2many('account.tax', 'product_taxes_rel', 'prod_id', 'tax_id', string='Customer Taxes',
        domain=[('type_tax_use', 'in', ('all','sale'))])
    supplier_taxes_id = fields.Many2many('account.tax', 'product_supplier_taxes_rel', 'prod_id', 'tax_id', string='Vendor Taxes',
        domain=[('type_tax_use', 'in', ('all','purchase'))])
    
class generic_tax_report(models.AbstractModel):
    _inherit = 'account.generic.tax.report'
    
    @api.model
    def get_lines(self, options, line_id=None):
        taxes = {}
        for tax in self.env['account.tax'].with_context(active_test=False).search([]):
            taxes[tax.id] = {'obj': tax, 'show': False, 'periods': [{'net': 0, 'tax': 0}]}
            for period in options['comparison'].get('periods'):
                taxes[tax.id]['periods'].append({'net': 0, 'tax': 0})
        period_number = 0
        self._compute_from_amls(options, taxes, period_number)
        for period in options['comparison'].get('periods'):
            period_number += 1
            self.with_context(date_from=period.get('date_from'), date_to=period.get('date_to'))._compute_from_amls(options, taxes, period_number)
        lines = []
        types = ['sale', 'purchase','all']
        groups = dict((tp, {}) for tp in types)
        for key, tax in taxes.items():
            if tax['obj'].type_tax_use == 'none':
                continue
            if tax['obj'].children_tax_ids:
                tax['children'] = []
                for child in tax['obj'].children_tax_ids:
                    if child.type_tax_use != 'none':
                        continue
                    tax['children'].append(taxes[child.id])
            if tax['obj'].children_tax_ids and not tax.get('children'):
                continue
            groups[tax['obj'].type_tax_use][key] = tax
        line_id = 0
        for tp in types:
            sign = tp == 'sale' and -1 or 1
            lines.append({
                    'id': tp,
                    'name': tp == 'sale' and _('Sale') or tp == 'purchase' and _('Purchase') or tp == 'all' and _('All'),
                    'unfoldable': False,
                    'columns': [{} for k in range(0, 2*(period_number+1) or 2)],
                    'level': 1,
                })
            for key, tax in sorted(groups[tp].items(), key=lambda k: k[1]['obj'].sequence):
                if tax['show']:
                    columns = []
                    for period in tax['periods']:
                        columns += [{'name': self.format_value(period['net'] * sign), 'style': 'white-space:nowrap;'},{'name': self.format_value(period['tax'] * sign), 'style': 'white-space:nowrap;'}]
                    lines.append({
                        'id': tax['obj'].id,
                        'name': tax['obj'].name + ' (' + str(tax['obj'].amount) + ')',
                        'unfoldable': False,
                        'columns': columns,
                        'level': 4,
                        'caret_options': 'account.tax',
                    })
                    for child in tax.get('children', []):
                        columns = []
                        for period in child['periods']:
                            columns += [{'name': self.format_value(period['net'] * sign), 'style': 'white-space:nowrap;'},{'name': self.format_value(period['tax'] * sign), 'style': 'white-space:nowrap;'}]
                        lines.append({
                            'id': child['obj'].id,
                            'name': '   ' + child['obj'].name + ' (' + str(child['obj'].amount) + ')',
                            'unfoldable': False,
                            'columns': columns,
                            'level': 4,
                            'caret_options': 'account.tax',
                        })
            line_id += 1
        return lines