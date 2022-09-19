# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields, api , _
from datetime import datetime, timedelta
from datetime import date
from odoo.exceptions import UserError, ValidationError
import calendar
from calendar import week
import dateutil.parser

MONTH_LIST = [('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec'),('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar')]


class FiscalPeriods(models.Model):
    _name = "fiscal.periods"
    _description = 'Fiscal Periods'
 
    name = fields.Char("Year")
    start_date_periods = fields.Date(string="Start Date")
    end_date_periods = fields.Date(string="End Date")
    documents_ids = fields.One2many('periods.generate', 'document_id', string="")
    documents_week_ids = fields.One2many('periods.week', 'document_week_id', string="")
    
    def daterange(self, a_start, b_end):
        for n in range(int ((b_end - a_start).days)):
            yield a_start + timedelta(n)
    
    @api.multi
    def generate_dates(self):
        line_ids = []
        for i in MONTH_LIST:
            quarter_per = 0
            if self.start_date_periods and self.end_date_periods:
                year_vals = datetime.strptime(self.start_date_periods,"%Y-%m-%d")
                year_val = year_vals.strftime('%Y')
                if i:
                    if int(i[0]) <= 3:
                        quarter_per = 4
                    if int(i[0]) > 3 and int(i[0]) <= 6:
                        quarter_per = 1 
                    if int(i[0]) > 6 and int(i[0]) <= 9:
                        quarter_per = 2
                    if int(i[0]) > 9 and int(i[0]) <= 12:
                        quarter_per = 3          
                    month_date = date(int(year_val), int(i[0]), 1)
                    date_from = month_date.replace(day=1)
                    date_to = month_date.replace(day=calendar.monthrange(month_date.year, month_date.month)[1])
                    if int(i[0]) <=3:
                        date_from  = date_from + dateutil.relativedelta.relativedelta(years=1)
                        date_to  = date_to + dateutil.relativedelta.relativedelta(years=1)
                        year_val = date_from.strftime('%Y')
                    vals = {
                            'month': int(i[0]),
                            'quarter':quarter_per,
                            'year':year_val,
                            'start_date':date_from,
                            'end_date':date_to,
                            } 
                    for del_recs in self.documents_ids:
                        if del_recs:
                            del_recs.unlink() 
                    line_ids.append((0, 0, vals))
                    
        self.update({'documents_ids': line_ids})
        return self.generate_weeks()
        
    @api.multi
    def generate_weeks(self): 
        if self.name:   
            if self.documents_week_ids:
                self.documents_week_ids.unlink()
#             for del_rec in self.documents_week_ids.unlink():
#                 if del_rec:
#                     del_rec.unlink()
                    
            line_week_ids = []
            a_start = date(int(self.name), 1, 1)
            b_end = date(int(self.name), 12, 31)
            week_count = 0
            week_start = 0
            week_end = 0
            i = 0
            week_end_last = 0
            for single_date in self.daterange(a_start, b_end):
                if i == 0:
                    week_start = single_date.strftime("%Y-%m-%d") 
                                     
                if single_date.strftime("%A") == 'Monday':
                    week_start = single_date.strftime("%Y-%m-%d")
                if week_start and single_date.strftime("%A") == 'Sunday':
                    week_end = single_date.strftime("%Y-%m-%d")
#                 if week_end == "2018-12-30" :
#                     week_start = "2018-12-31"
#                     week_end = "2018-12-31"
                   
                   
#                  if week_start  single_date.strftime("%A")=='Sunday':
#                     week_end = single_date.strftime("%Y-%m-%d")    
                i += 1
                if week_end != 0 and week_start != 0:
                    week_count += 1
                    month_count1 = datetime.strptime(week_start, '%Y-%m-%d').strftime('%m')
                    month_count2 = datetime.strptime(week_end, '%Y-%m-%d').strftime('%m')
                    if month_count2 > month_count1:
                        rec_count = month_count2
                        week_end_last = month_count1  
                    if month_count2 == month_count1:
                        rec_count = month_count2
                        week_end_last = month_count2   
                    vals = {
                           
                            'year': int(self.name),
                            'month':week_end_last,
                            'month_name': 'M' + str(rec_count) + '-' + str(self.name),
                            'week':week_count,
                            'week_name': 'W' + str(week_count),
                            'start_date':week_start,
                            'end_date':week_end,
                            }
                   
                    week_start = 0
                    if week_end =="2018-12-30":
                        week_start = "2018-12-31"
                    week_end = 0
                    line_week_ids.append((0, 0, vals))
                    
                    
            if week_start != 0 and week_end == 0:
                week_count_last = week_count + 1
                vals = {
                       
                        'year': int(self.name),
                        'month':week_end_last,
                        'month_name': 'M' + str(week_end_last) + '-' + str(self.name),
                        'week':week_count_last,
                        'week_name': 'W' + str(week_count_last),
                        'start_date':week_start,
                        'end_date':b_end,
                        }
                week_start = 0
                week_end = 0
                line_week_ids.append((0, 0, vals))
            
            
            self.update({'documents_week_ids': line_week_ids})  
            
    @api.model
    def fiscal_periods_send_cron(self):
        invoice_id = self.env['account.invoice'].search([])
        for vals_invoice in invoice_id:
            if vals_invoice.date_invoice:
                year_rec = datetime.strptime(vals_invoice.date_invoice, '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(vals_invoice.date_invoice, '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(vals_invoice.date_invoice, '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(vals_invoice.date_invoice, '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for line in fiscal_period_id:
                    if line:
                        vals_invoice.year = line.year
                        vals_invoice.month =  'M'+str(line.month)
#                         vals_invoice.week = line.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        vals_invoice.quarter = 'Q' + '-' + '0' + str(line.quarter) 
        
        move_id = self.env['account.move'].search([])
        for vals_move in move_id:
            if vals_move.date:
                year_rec = datetime.strptime(vals_move.date, '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(vals_move.date, '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(vals_move.date, '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(vals_move.date, '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for line in fiscal_period_id:
                    if line:
                        vals_move.year = line.year
                        vals_move.month =  'M'+str(line.month)
#                         vals_move.week = line.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        vals_move.quarter = 'Q' + '-' + '0' + str(line.quarter)    
                                               
        payment_id = self.env['account.payment'].search([])
        for vals_payment in payment_id:
            if vals_payment.payment_date:
                year_rec = datetime.strptime(vals_payment.payment_date, '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(vals_payment.payment_date, '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(vals_payment.payment_date, '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(vals_payment.payment_date, '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for line in fiscal_period_id:
                    if line:
                        vals_payment.year = line.year
                        vals_payment.month =  'M'+str(line.month)
#                         vals_payment.week = line.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        vals_payment.quarter = 'Q' + '-' + '0' + str(line.quarter)    
            
    
class GeneratePeriods(models.Model):
    _name = "periods.generate"  
    
    document_id = fields.Many2one("fiscal.periods")    
    month = fields.Integer("Month")  
    quarter = fields.Integer("Quarter")
    year = fields.Char("Year")
    start_date = fields.Date("Starting Date")
    end_date = fields.Date("Ending Date")


class GeneratePeriodsWeek(models.Model):
    _name = "periods.week"  
    _rec_name = 'month_name'
    
    document_week_id = fields.Many2one("fiscal.periods") 
    year = fields.Char("Year")   
    month = fields.Integer("Month")
    month_name = fields.Char("Month")
    week = fields.Integer("Week")
    week_name = fields.Char("Week")
    start_date = fields.Date("Starting Date")
    end_date = fields.Date("Ending Date")


class SaleOrder(models.Model):
    _inherit = "sale.order"
     
    year = fields.Char("Year")
    quarter = fields.Char("Quarter")
    month = fields.Char("Month")
    week = fields.Char("Week")
    
    @api.model
    def create(self, values):
        if 'validity_date' in values:
            if values['validity_date']:
                year_rec = datetime.strptime(values['validity_date'], '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(values['validity_date'], '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(values['validity_date'], '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(values['validity_date'], '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for line in fiscal_period_id:
                    if line:
                        values['year'] = line.year
                        values['month'] = 'M'+str(line.month)
#                         values['week'] = line.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        values['quarter'] = 'Q' + '-' + '0' + str(line.quarter)       
        record = super(SaleOrder, self).create(values)                   
        return record 
    
    @api.multi
    def write(self, vals):
        if 'validity_date' in vals:
            if vals.get('validity_date'):
                year_rec = datetime.strptime(vals.get('validity_date'), '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(vals.get('validity_date'), '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(vals.get('validity_date'), '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(vals.get('validity_date'), '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for lines in fiscal_period_id:
                    if lines:
                        vals['year'] = lines.year
                        vals['month'] = 'M'+str(lines.month)
#                         vals['week'] = lines.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        vals['quarter'] = 'Q' + '-' + '0' + str(lines.quarter)    
        return super(SaleOrder, self).write(vals)

    
class Lead(models.Model):
    _inherit = "crm.lead"  
    
    year = fields.Char("Year")
    quarter = fields.Char("Quarter")
    month = fields.Char("Month")
    week = fields.Char("Week")
    
    @api.model
    def create(self, values):
        if 'date_deadline' in values:
            if values['date_deadline']:
                print(values['date_deadline'])
                year_rec = datetime.strptime(values['date_deadline'], '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(values['date_deadline'], '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(values['date_deadline'], '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(values['date_deadline'], '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for line in fiscal_period_id:
                    if line:
                        values['year'] = line.year
                        values['month'] = 'M'+str(line.month)
#                         values['week'] = line.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        values['quarter'] = 'Q' + '-' + '0' + str(line.quarter) 
        record = super(Lead, self).create(values)                   
        return record 
    
    @api.multi
    def write(self, vals):
        if 'date_deadline' in vals:
            if vals['date_deadline']:
                year_rec = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(vals.get('date_deadline'), '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for lines in fiscal_period_id:
                    if lines:
                        vals['year'] = lines.year
                        vals['month'] = 'M'+str(lines.month)
#                         vals['week'] = lines.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        vals['quarter'] = 'Q' + '-' + '0' + str(lines.quarter) 
        return super(Lead, self).write(vals)
    
    
class AccountInvoice(models.Model):
    _inherit = "account.invoice"    

    year = fields.Char("Year")
    quarter = fields.Char("Quarter")
    month = fields.Char("Month")
    week = fields.Char("Week")
        
    @api.model
    def create(self, values):
        if 'date_invoice' in values:
            if values['date_invoice']:
                year_rec = datetime.strptime(values['date_invoice'], '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(values['date_invoice'], '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(values['date_invoice'], '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(values['date_invoice'], '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for line in fiscal_period_id:
                    if line:
                        values['year'] = line.year
                        values['month'] = 'M'+str(line.month)
#                         values['week'] = line.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        values['quarter'] = 'Q' + '-' + '0' +  str(line.quarter) 
        record = super(AccountInvoice, self).create(values)                   
        return record 
    
    @api.multi
    def write(self, vals):
        if 'date_invoice' in vals:
            if vals.get('date_invoice'):
                year_rec = datetime.strptime(vals.get('date_invoice'), '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(vals.get('date_invoice'), '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(vals.get('date_invoice'), '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(vals.get('date_invoice'), '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for lines in fiscal_period_id:
                    if lines:
                        vals['year'] = lines.year
                        vals['month'] = 'M'+str(lines.month)
#                         vals['week'] = lines.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        vals['quarter'] = 'Q' + '-' + '0' +  str(lines.quarter) 
        return super(AccountInvoice, self).write(vals)

    
class account_payment(models.Model):
    _inherit = "account.payment"   
    
    year = fields.Char("Year")
    quarter = fields.Char("Quarter")
    month = fields.Char("Month")
    week = fields.Char("Week")
    
    @api.model
    def create(self, values):
        if 'payment_date' in values:
            if values['payment_date']:
                year_rec = datetime.strptime(values['payment_date'], '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(values['payment_date'], '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(values['payment_date'], '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(values['payment_date'], '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for line in fiscal_period_id:
                    if line:
                        values['year'] = line.year
                        values['month'] = 'M'+str(line.month)
#                         values['week'] = line.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        values['quarter'] = 'Q' + '-' + '0' + str(line.quarter) 
        record = super(account_payment, self).create(values)                   
        return record 
    
    @api.multi
    def write(self, vals):
        if 'payment_date' in vals:
            if vals.get('payment_date'):
                year_rec = datetime.strptime(vals.get('payment_date'), '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(vals.get('payment_date'), '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(vals.get('payment_date'), '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(vals.get('payment_date'), '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for lines in fiscal_period_id:
                    if lines:
                        vals['year'] = lines.year
                        vals['month'] = 'M'+str(lines.month)
#                         vals['week'] = lines.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        vals['quarter'] = 'Q' + '-' + '0' + str(lines.quarter) 
        return super(account_payment, self).write(vals)

    
class AccountMove(models.Model):
    _inherit = "account.move" 
    
    year = fields.Char("Year")
    quarter = fields.Char("Quarter")
    month = fields.Char("Month")
    week = fields.Char("Week")
    
    @api.model
    def create(self, values):
        if 'date' in values:
            if values['date']:
                year_rec = datetime.strptime(values['date'], '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(values['date'], '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(values['date'], '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(values['date'], '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for line in fiscal_period_id:
                    if line:
                        values['year'] = line.year
                        values['month'] = 'M'+str(line.month)
#                         values['week'] = line.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        values['quarter'] = 'Q' + '-' + '0' + str(line.quarter) 
        record = super(AccountMove, self).create(values)                   
        return record 
    
    @api.multi
    def write(self, vals):
        if 'date' in vals:
            if vals.get('date'):
                year_rec = datetime.strptime(vals.get('date'), '%Y-%m-%d').strftime('%Y')
                month_rec = datetime.strptime(vals.get('date'), '%Y-%m-%d').strftime('%m')
    
                fiscal_period_id = self.env['periods.generate'].search([
                        ('year', '=', year_rec),
                        ('start_date', '<=', datetime.strptime(vals.get('date'), '%Y-%m-%d').strftime('%Y-%m-%d')),
                        ('end_date', '>=', datetime.strptime(vals.get('date'), '%Y-%m-%d').strftime('%Y-%m-%d'))])
                for lines in fiscal_period_id:
                    if lines:
                        vals['year'] = lines.year
                        vals['month'] = 'M'+str(lines.month)
#                         vals['week'] = lines.week_name
                        if int(month_rec) <= 3:
                                quarter_per = 1
                        if int(month_rec) > 3 and int(month_rec) <= 6:
                            quarter_per = 2 
                        if int(month_rec) > 6 and int(month_rec) <= 9:
                            quarter_per = 3
                        if int(month_rec) > 9 and int(month_rec) <= 12:
                            quarter_per = 4   
                        vals['quarter'] = 'Q' + '-' + '0' + str(lines.quarter) 
        return super(AccountMove, self).write(vals)  

    
class AccountMoveLine(models.Model):
    _inherit = "account.move.line" 
    
    year = fields.Char("Year", related='move_id.year', store=True)
    quarter = fields.Char("Quarter", related='move_id.quarter', store=True)
    month = fields.Char("Month", related='move_id.month', store=True)
    week = fields.Char("Week")    
      
    
