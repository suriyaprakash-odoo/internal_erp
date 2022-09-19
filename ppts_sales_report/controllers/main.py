from odoo import http
from odoo.http import request
from datetime import datetime

class PipelineWebReport(http.Controller):
    @http.route(['/ppts_sales_report_web_view/'], type='http', auth='public', website=True)
    def view_pipeline_report(self,**post):
        invoice_ids = request.env['account.invoice'].sudo().search([('id','in', request.session['invoice_list'])],order='date_invoice asc')
        start_dt = datetime.strptime(request.session['date_from'], '%Y-%m-%d')
        start_date = start_dt.strftime("%d-%m-%Y")
        end_dt = datetime.strptime(request.session['date_to'], '%Y-%m-%d')
        end_date = end_dt.strftime("%d-%m-%Y")

        return_values = {
            'date': datetime.today().date(),
            'invoices':invoice_ids,
            'start_date':start_date,
            'end_date':end_date,
        }
        return request.render('ppts_sales_report.ppts_sales_report_web_view', return_values)

