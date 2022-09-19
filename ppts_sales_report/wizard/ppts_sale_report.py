from odoo import api, fields, models, _
from datetime import datetime
import base64
import xlwt
from odoo.http import request
from urllib.parse import urljoin
from odoo.exceptions import UserError
import psutil

class PptsSaleReport(models.TransientModel):
    _name = "ppts.sale.report"

    partner_ids = fields.Many2many("res.partner",string="Customer")
    all_partner = fields.Boolean("Select All Customers",default=True)
    date_from = fields.Date("Date From",required=True)
    date_to = fields.Date("Date To",required=True)
    paid_state = fields.Boolean("Paid",default=True)
    open_state = fields.Boolean("Open",default=True)
    cancel_state = fields.Boolean("Cancel",default=True)
    xl_file = fields.Binary(" Download File")
    xl_name = fields.Char("File name")

    @api.multi
    def generate_xl_report(self):
        workbook = xlwt.Workbook()
        xlwt.add_palette_colour("custom_colour", 0x20)
        xlwt.add_palette_colour("custom_colour0", 0x21)
        xlwt.add_palette_colour("custom_colour1", 0x22)
        xlwt.add_palette_colour("custom_colour2", 0x16)
        xlwt.add_palette_colour("custom_colour3", 0x09)
        xlwt.add_palette_colour("custom_colour4", 0x10)
        workbook.set_colour_RGB(0x20, 255, 153, 51)
        workbook.set_colour_RGB(0x21, 242, 242, 242)
        workbook.set_colour_RGB(0x22, 113, 178, 226)
        workbook.set_colour_RGB(0x16, 233, 238, 242)
        workbook.set_colour_RGB(0x09, 255, 255, 247)
        workbook.set_colour_RGB(0x10, 235, 237, 237)

        sheet = workbook.add_sheet("Sales Report", cell_overwrite_ok=True)
        sheet.show_grid = False
        sheet.col(1).width = 256 * 10
        sheet.col(2).width = 256 * 15
        sheet.col(3).width = 256 * 15
        sheet.col(4).width = 256 * 15
        sheet.col(5).width = 256 * 15
        sheet.col(6).width = 256 * 20
        sheet.col(7).width = 256 * 20
        sheet.col(10).width = 256 * 10
        sheet.col(11).width = 256 * 15
        sheet.col(13).width = 256 * 17

        date_from = self.date_from
        date_to = self.date_to
        state_domain=[]

        if self.paid_state:
            state_domain.append('paid')
        if self.open_state:
            state_domain.append('open')
        if self.cancel_state:
            state_domain.append('cancel')
        if not self.paid_state and not self.open_state and not self.cancel_state:
            raise UserError(_('Please select any state(Paid/Open/Cancel)'))

        if self.all_partner:
            invoice_ids = self.env['account.invoice'].search([('state', 'in', state_domain),('date_invoice','<=',date_to),('date_invoice','>=',date_from),
                                                              ('type','=','out_invoice')], order='date_invoice asc')
        else:
            invoice_ids = self.env['account.invoice'].search([('partner_id', 'in', [x.id for x in self.partner_ids]),
                                                              ('state','in',state_domain),('date_invoice','<=',date_to),
                                                              ('date_invoice','>=',date_from),('type','=','out_invoice')],order='date_invoice asc')
        if not invoice_ids:
            raise UserError(_('No records found for the given condition'))

        n = 7
        i = 0

        temp_inv_month = False
        start_row = False
        end_row = False

        style0 = xlwt.easyxf(
            'font: name Century Gothic, height 300,bold True;align: horiz center;pattern:pattern solid,fore-colour custom_colour0;',
            num_format_str='DD-MM-YYYY')
        style01 = xlwt.easyxf(
            'font: name Century Gothic, colour white, bold True;pattern:pattern solid,fore-colour custom_colour;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,'
            'left thin,right thin,top thin,bottom thin;align: vert centre, wrap on',
            num_format_str='"$"#,##0.00')
        style10 = xlwt.easyxf(
            'font: name Century Gothic, colour black, bold True;pattern:pattern solid,fore-colour custom_colour4;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,'
            'left thin,right thin,top thin,bottom thin;align:wrap on,vert centre, horiz right',
            num_format_str='"$"#,##0.00')
        style001 = xlwt.easyxf(
            'font: name Century Gothic; pattern:pattern solid,fore-colour custom_colour3;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,left thin,right thin,top thin,bottom thin;align: vert top; align:wrap on;align: horiz right',
            num_format_str='"₹"#,##0.00')
        style002 = xlwt.easyxf(
            'font: name Century Gothic; pattern:pattern solid,fore-colour custom_colour2;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,left thin,right thin,top thin,bottom thin;align: vert top; align:wrap on;align: horiz right'
            , num_format_str='"₹"#,##0.00')
        for invoice in invoice_ids:

            style02 = xlwt.easyxf(
                'font: name Century Gothic; pattern:pattern solid,fore-colour custom_colour3;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,left thin,right thin,top thin,bottom thin;align: vert top; align:wrap on;'
                , num_format_str=invoice.currency_id.symbol + '""#,##0.00')

            style03 = xlwt.easyxf(
                'font: name Century Gothic; pattern:pattern solid,fore-colour custom_colour2;border:top_color gray40, bottom_color gray40, right_color gray40, left_color gray40,left thin,right thin,top thin,bottom thin;align: vert top; align:wrap on;'
                , num_format_str=invoice.currency_id.symbol + '""#,##0.00')

            start_dt = datetime.strptime(self.date_from, '%Y-%m-%d')
            start_date = start_dt.strftime("%d-%m-%Y")
            end_dt = datetime.strptime(self.date_to, '%Y-%m-%d')
            end_date = end_dt.strftime("%d-%m-%Y")

            sheet.write_merge(2, 3, 1, 13,'SALES REPORT ' + '(' + str(start_date) + '  -  ' + str(end_date) + ')', style0)
            sheet.row(6).height_mismatch = True
            sheet.row(6).height = 64 * 8

            sheet.write(6, 1, 'Month', style01)
            sheet.write(6, 2, 'Invoice Reference Number', style01)
            sheet.write(6, 3, 'Invoice Date', style01)
            sheet.write(6, 4, 'NSDL Reference No.', style01)
            sheet.write(6, 5, 'Soft Tex Form No.', style01)
            sheet.write(6, 6, 'Client Name', style01, )
            sheet.write(6, 7, 'Address', style01)
            sheet.write(6, 8, 'Country', style01)
            sheet.write(6, 9, 'Country Code', style01)
            sheet.write(6, 10, 'Currency', style01)
            sheet.write(6, 11, 'Value', style01)
            sheet.write(6, 12, 'Ex.Rate', style01)
            sheet.write(6, 13, 'Invoice Value INR', style01)

            inv_date = datetime.strptime(invoice.date_invoice, '%Y-%m-%d')
            inv_month = inv_date.strftime("%b-%y")
            invoice_date = str(inv_date.strftime("%d-%m-%Y"))

            if not temp_inv_month and not start_row and not end_row:
                temp_inv_month = inv_month
                start_row = n
                end_row = n

            if inv_month == temp_inv_month:
                end_row = n
            else:
                start_row = n
                end_row = n
                temp_inv_month = inv_month

            if i == 0:
                new_style = style02
                new_style1 = style001
                i = 1
            else:
                new_style = style03
                new_style1 = style002
                i = 0

            sheet.write_merge(start_row, end_row, 1, 1, inv_month or '', style10)
            sheet.write(n, 2, invoice.number or '', new_style)
            sheet.write(n, 3, invoice_date or '', new_style)
            sheet.write(n, 4, invoice.nsdl_ref_no or '', new_style)
            sheet.write(n, 5, invoice.softex_no or '', new_style)
            sheet.write(n, 6, invoice.partner_id.name or '', new_style)
            sheet.write(n, 7, str(invoice.partner_id.street or '') + str(invoice.partner_id.city or '')
                        + str(invoice.partner_id.state_id.name or '') or '' , new_style)
            sheet.write(n, 8, invoice.partner_id.country_id.name or '', new_style)
            sheet.write(n, 9, invoice.partner_id.country_id.code or '', new_style)
            sheet.write(n, 10, invoice.currency_id.name or '', new_style)
            sheet.write(n, 11, invoice.amount_total or '', new_style)
            sheet.write(n, 12, invoice.currency_rate or (1/invoice.currency_id.rate) or '', new_style1)
            sheet.write(n, 13, invoice.move_id.amount or '', new_style1)
            n += 1

        if psutil.LINUX:
            f_name = ('/tmp/Sales Report-' + str(datetime.today().date()) + '.xls')
        else:
            f_name = ('Sales Report-' + str(datetime.today().date()) + '.xls')

        workbook.save(f_name)
        fp = open(f_name, "rb")
        file_data = fp.read()
        out = base64.encodestring(file_data)

        if psutil.LINUX:
            filename = f_name.split('/')[2]
        else:
            filename = f_name.split('/')[0]

        attach_vals = {
            'xl_file': out,
            'xl_name': filename,
            'all_partner': self.all_partner,
            'partner_ids': [(6, False, [x.id for x in self.partner_ids])],
            'date_from': self.date_from,
            'date_to': self.date_to,
            'paid_state':self.paid_state,
            'open_state':self.open_state,
            'cancel_state':self.cancel_state
        }

        act_id = self.env['ppts.sale.report'].create(attach_vals)
        fp.close()

        return {
            'name': _('Sales Report'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'ppts.sale.report',
            'target': 'new',
            'res_id': act_id.id,
        }

    @api.multi
    def preview_report(self):
        base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
        page_url = urljoin(base_url, "ppts_sales_report_web_view")

        state_domain = []

        if self.paid_state:
            state_domain.append('paid')
        if self.open_state:
            state_domain.append('open')
        if self.cancel_state:
            state_domain.append('cancel')

        if not self.paid_state and not self.open_state and not self.cancel_state:
            raise UserError(_('Please select any state(Paid/Open/Cancel)'))

        if self.all_partner:
            invoice_ids = self.env['account.invoice'].search([('state', 'in', state_domain),
                                                              ('date_invoice', '<=', self.date_to),
                                                              ('date_invoice', '>=', self.date_from),
                                                              ('type', '=', 'out_invoice')], order='date_invoice asc')
        else:
            invoice_ids = self.env['account.invoice'].search([('partner_id', 'in', [x.id for x in self.partner_ids]),('state','in',state_domain),
                                                              ('date_invoice', '<=', self.date_to), ('date_invoice', '>=', self.date_from),
                                                              ('type', '=', 'out_invoice')],order='date_invoice asc')

        request.session['invoice_list'] = invoice_ids.ids
        request.session['date_from'] =  self.date_from
        request.session['date_to'] = self.date_to

        return {
            'type': 'ir.actions.act_url',
            'name': "Sales Web Report",
            'target': '_blank',
            'url': page_url
        }