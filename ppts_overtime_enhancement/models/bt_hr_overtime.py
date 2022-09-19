
from odoo import fields, api, models, _
from datetime import date,datetime,timedelta
from ast import literal_eval
import datetime
import time
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta



class BtHrOvertime(models.Model):   
    _name = "bt.hr.overtime"
    _description = "Bt Hr Overtime" 
    _rec_name = 'employee_id'
    _order = 'id desc'
    
    employee_id = fields.Many2one('hr.employee', string="Employee")
    manager_id = fields.Many2one('hr.employee', string='Manager')
    start_date = fields.Datetime('Date')
    overtime_hours = fields.Float('Overtime Hours')
    notes = fields.Text(string='Notes')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Waiting Approval'), ('refuse', 'Refused'), 
           ('validate', 'Approved'), ('cancel', 'Cancelled')], default='draft', copy=False)
    attendance_id = fields.Many2one('hr.attendance', string='Attendance')
    
    @api.model
    def run_overtime_scheduler(self):
        """ This Function is called by scheduler. """
        current_date = date.today()
        working_hours_empl = self.env['hr.contract']
        attend_signin_ids = self.env['hr.attendance'].search([('overtime_created', '=', False)])
        records =  self.env['ir.config_parameter'].sudo().get_param("ppts_overtime_enhancement.minimum_overtime_hours")
        
        
        emp_ids = self.env['hr.employee'].search([('over_time_hours','=',True)])
        if emp_ids:
            for emp in emp_ids:
                today_date = date.today()
                print('today_date',today_date)
                
                self._cr.execute(''' select sum(worked_hours) from hr_attendance where employee_id = %s and check_in::date = '%s' and check_out::date = '%s' '''%(emp.id,today_date,today_date))
                rows = self._cr.dictfetchall()
                print("rowsrowsrows",rows)
                if rows and rows[0]['sum'] != None:
                    tot_wrkd_hrs = rows[0]['sum']
                                       
                    contract_obj = self.env['hr.contract'].search([('employee_id', '=', emp.id),('work_hours','!=',0)])
                    print (contract_obj.employee_id.name,'ff')
                    for contract in contract_obj:
                        working_hours = contract.work_hours
                        worked_hour_att = tot_wrkd_hrs
                        print (working_hours,'ttt')
                        if worked_hour_att > working_hours:
                            overtime_hours = worked_hour_att - working_hours
                            if overtime_hours >= float(records):
                                vals = {
                                     'employee_id':emp.id and emp.id or False,
                                     'manager_id' : emp.id and emp.parent_id and emp.parent_id.id or False,
                                     'start_date' : today_date,
                                     'overtime_hours': round(overtime_hours,2),
                                     
                                     }
                                test = self.env['bt.hr.overtime'].create(vals)
                               
#                                 obj.overtime_created = True
                    
#                 attend_ids = self.env['hr.attendance'].search([('check_in', '>=', today_date),('check_out','<=',today_date),('employee_id','=',emp.id)])
#                 if attend_ids:
#                     actual_working_hours = 0
#                     for att in attend_ids:
#                         actual_working_hours += att.worked_hours
#                         print('actual_working_hours',actual_working_hours)
        
#         for obj in attend_signin_ids:
#             if obj.check_in and obj.check_out:
#                 start_date = datetime.datetime.strptime(obj.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
#                 print(start_date,'ss')
#                 end_date = datetime.datetime.strptime(obj.check_out, DEFAULT_SERVER_DATETIME_FORMAT) 
#                 print(end_date,'vv')
#                 difference = end_date - start_date
#                 print(difference,'dd')
#                 hour_diff = str(difference).split(':')[0]
#                 print(hour_diff,'hh')
#                 min_diff = str(difference).split(':')[1]
#                 print(min_diff,'hh')
#                 tot_diff = hour_diff + '.' + min_diff
#                 print(tot_diff,'tt')
#                 actual_working_hours = float(tot_diff)
#                 print(actual_working_hours,'ww')
#                 if obj.employee_id.over_time_hours == True:
#                     contract_obj = self.env['hr.contract'].search([('employee_id', '=', obj.employee_id.id),('work_hours','!=',0)])
#                     print (contract_obj.employee_id.name,'ff')
#                     for contract in contract_obj:
#                         working_hours = contract.work_hours
#                         worked_hour_att = obj.worked_hours
#                         print (working_hours,'ttt')
#                         if worked_hour_att > working_hours:
#                             overtime_hours = worked_hour_att - working_hours
#                             if overtime_hours >= float(records):
#                                 vals = {
#                                      'employee_id':obj.employee_id and obj.employee_id.id or False,
#                                      'manager_id' : obj.employee_id and obj.employee_id.parent_id and obj.employee_id.parent_id.id or False,
#                                      'start_date' : obj.check_in,
#                                      'overtime_hours': round(overtime_hours,2),
#                                      'attendance_id': obj.id,
#                                      }
#                                 test = self.env['bt.hr.overtime'].create(vals)
#                                 print('-------------',test)
#                                 obj.overtime_created = True
                    
    @api.multi
    def action_submit(self):
        return self.write({'state':'confirm'})
        
    @api.multi
    def action_cancel(self):
        return self.write({'state':'cancel'})
        
    @api.multi
    def action_approve(self):
        return self.write({'state':'validate'})
    
    @api.multi
    def action_refuse(self):
        return self.write({'state':'refuse'})
        
    @api.multi
    def action_view_attendance(self):
        attendances = self.mapped('attendance_id')
        action = self.env.ref('hr_attendance.hr_attendance_action').read()[0]
        if len(attendances) > 1:
            action['domain'] = [('id', 'in', attendances.ids)]
        elif len(attendances) == 1:
            action['views'] = [(self.env.ref('hr_attendance.hr_attendance_view_form').id, 'form')]
            action['res_id'] = self.attendance_id.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
        

class Contract(models.Model):
    _inherit = 'hr.contract'
    
    work_hours = fields.Float(string='Working Hours')
    
    
class HrAttendance(models.Model):
    _inherit = "hr.attendance" 
    
    overtime_created = fields.Boolean(string = 'Overtime Created', default=False, copy=False)
    
