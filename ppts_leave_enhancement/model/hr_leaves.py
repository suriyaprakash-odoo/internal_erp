from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError, ValidationError
from datetime import datetime
from datetime import date
import math
from datetime import datetime, timedelta

HOURS_PER_DAY = 8



class Holidays(models.Model):
    _inherit = "hr.holidays"
    
    request_unit_half = fields.Boolean('Half Day')
    duration_hours = fields.Float('Duration Hours', default=8.00)

    request_date_from_period = fields.Selection([('am', 'Morning'), ('pm', 'Afternoon')], string="Date Period Start"
                                                ,default ="am")
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
       
    @api.onchange('request_unit_half')
    def _onchange_unit_time(self):
        if self.request_unit_half == True:
            self.number_of_days_temp = 0.5
         
            if self.number_of_days_temp == 0.5:
                self.duration_hours = 4.00
        elif self.request_unit_half == False:
            self.duration_hours = 8.00
                     
    def _get_number_of_days(self, date_from, date_to, employee_id):
        """ Returns a float equals to the timedelta between two dates given as string."""
        from_dt = fields.Datetime.from_string(date_from)
        to_dt = fields.Datetime.from_string(date_to)

#         if employee_id:
#             employee = self.env['hr.employee'].browse(employee_id)
#             return employee.get_work_days_count(from_dt, to_dt)
# 
#         time_delta = to_dt - from_dt
#         return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)
# 
#     @api.onchange('date_from')
#     def _onchange_date_from(self):
#         """ If there are no date set for date_to, automatically set one 8 hours later than
#             the date_from. Also update the number_of_days.
#         """
#         date_from = self.date_from
#         date_to = self.date_to
# 
#         # No date_to set so far: automatically compute one 8 hours later
#         if date_from and not date_to:
#             date_to_with_delta = fields.Datetime.from_string(date_from) + timedelta(hours=HOURS_PER_DAY)
#             self.date_to = str(date_to_with_delta)
# 
#         # Compute and update the number of days
#         if (date_to and date_from) and (date_from <= date_to):
#             self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
#         else:
#             self.number_of_days_temp = 0

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """ Update the number_of_days. """
        date_from = self.date_from
        date_to = self.date_to

        # Compute and update the number of days
#         if (date_to and date_from) and (date_from <= date_to):
#             self.number_of_days_temp = self._get_number_of_days(date_from, date_to, self.employee_id.id)
#         else:
#             self.number_of_days_temp = 0
    
    @api.onchange('date_from', 'date_to','number_of_days_temp')
    def _onchange_date_time(self):
        if self.date_from and self.date_to:
            date_f = datetime.strptime(self.date_from,  "%Y-%m-%d")
            date_t = datetime.strptime(self.date_to,  "%Y-%m-%d")
            delta = (date_t - date_f)
            print ('ddd',delta.days)
            days = delta + timedelta(days=1)
            print (days,'ffffff')
            
            if not self.request_unit_half:
                self.number_of_days_temp = days.days
                self.duration_hours =  days.days*8
            else:
                self.number_of_days_temp = 0.5
            
                            
     
    @api.multi
    def _prepare_holidays_meeting_values(self):
        if not self.request_unit_half:
            self.ensure_one()
            meeting_values = {
                'name': self.display_name,
                'categ_ids': [(6, 0, [
                    self.holiday_status_id.categ_id.id])] if self.holiday_status_id.categ_id else [],
                'duration': self.number_of_days_temp * HOURS_PER_DAY,
                'description': self.notes,
                'user_id': self.user_id.id,
                'start': self.date_from,
                'stop': self.date_to,
                'allday': False,
                'state': 'open',  # to block that meeting date in the calendar
                'privacy': 'confidential'
            }
            # Add the partner_id (if exist) as an attendee
            if self.user_id and self.user_id.partner_id:
                meeting_values['partner_ids'] = [
                    (4, self.user_id.partner_id.id)]
            return meeting_values 

        else:
            self.ensure_one()
            meeting_values = {
                'name': self.display_name,
                'categ_ids': [(6, 0, [
                    self.holiday_status_id.categ_id.id])] if self.holiday_status_id.categ_id else [],
                'duration': self.number_of_days_temp * HOURS_PER_DAY,
                'description': self.notes,
                'user_id': self.user_id.id,
                'start': self.date_from,
                'stop': self.date_from,
                'allday': False,
                'state': 'open',  # to block that meeting date in the calendar
                'privacy': 'confidential'
            }
            # Add the partner_id (if exist) as an attendee
            if self.user_id and self.user_id.partner_id:
                meeting_values['partner_ids'] = [
                    (4, self.user_id.partner_id.id)]
            return meeting_values 
   
              
            
            
            
    
