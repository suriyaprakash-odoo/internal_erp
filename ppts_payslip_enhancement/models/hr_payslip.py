# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
from datetime import time as datetime_time
from dateutil import relativedelta
from datetime import timedelta  

import babel

from odoo import api, fields, models, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.onchange('employee_id', 'date_from', 'date_to')
    def onchange_employee(self):

        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return

        employee = self.employee_id
        date_from = self.date_from
        date_to = self.date_to
        contract_ids = []

        ttyme = datetime.fromtimestamp(time.mktime(time.strptime(date_from, "%Y-%m-%d")))
        locale = self.env.context.get('lang') or 'en_US'
        self.name = _('Salary Slip of %s for %s') % (employee.name, tools.ustr(babel.dates.format_date(date=ttyme, format='MMMM-y', locale=locale)))
        self.company_id = employee.company_id

        if not self.env.context.get('contract') or not self.contract_id:
            contract_ids = self.get_contract(employee, date_from, date_to)
            if not contract_ids:
                return
            self.contract_id = self.env['hr.contract'].browse(contract_ids[0])

        if not self.contract_id.struct_id:
            return
        self.struct_id = self.contract_id.struct_id

        #computation of the salary input
        contracts = self.env['hr.contract'].browse(contract_ids)
        worked_days_line_ids = self.get_worked_day_lines(contracts, date_from, date_to)
        worked_days_lines = self.worked_days_line_ids.browse([])
        for r in worked_days_line_ids:
            worked_days_lines += worked_days_lines.new(r)
            
        #Added by jana# calculation of presented days. 
        attend_ids = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('check_in', '<=', date_to), ('check_in', '>=', date_from)])
        date_format = "%Y-%m-%d"
        date_from = datetime.strptime(date_from, date_format)
        date_to = datetime.strptime(date_to, date_format)
        days = date_to - date_from
        date_from =date_from.date()
        total_days = 0
        total_hours = 0
        for day in range(days.days):
            attend_ids = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('check_in', '<=', datetime.strftime(date_from, date_format)), ('check_in', '>=', datetime.strftime(date_from, date_format))])
            if attend_ids:
                hours = sum(attend_ids.mapped("worked_hours"))
                if hours >= 6:
                    total_days = total_days+1;
                elif hours < 6 and hours >= 4:
                    total_days = total_days+1;
                total_hours = total_hours+hours;
            date_from = date_from + timedelta(days=1)
            
            
        attendances = {
                'name': _("Present Days"),
                'sequence': 3,
                'code': 'PRENTDAYS',
                'number_of_days': total_days,
                'number_of_hours': total_hours,
                'contract_id': self.contract_id.id,
            }
        worked_days_lines += self.worked_days_line_ids.browse([]).new(attendances)
        self.worked_days_line_ids = worked_days_lines
        

        input_line_ids = self.get_inputs(contracts, date_from, date_to)
        input_lines = self.input_line_ids.browse([])
        for r in input_line_ids:
            input_lines += input_lines.new(r)
        self.input_line_ids = input_lines
        return

