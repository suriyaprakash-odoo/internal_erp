from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import time

# hr.employee form

class Employee(models.Model):
    _inherit = "hr.employee"
    
    appraisal_by_ro = fields.Many2one('hr.employee', 'RO')        
    appraisal_by_tl = fields.Boolean(string='TL') 
       
    appraisal_tl_ids = fields.Many2many('hr.employee', 'emp_appraisal_manager_rels', 'hr_appraisal_id')   
    appraisal_tl_id  = fields.Many2one('survey.survey', 'Appraisal Tl')
    
    appraisals_by_ro = fields.Boolean(string='RO')
    appraisal_ro_ids = fields.Many2many('hr.employee', 'emp_appraisal_ro_rel', 'hr_appraisal_id')
    appraisal_ro_id  = fields.Many2one('survey.survey', 'Appraisal Ro')
   
    appraisals_by_hr = fields.Boolean(string='HR')   
    appraisal_hr_ids = fields.Many2many('hr.employee', 'emp_appraisal_hr_rel', 'hr_appraisal_id' , domain=[('manager', '=', True)])
    appraisal_hr_id  = fields.Many2one('survey.survey', 'Appraisal Tl')
   
 
    @api.onchange('appraisal_by_tl', 'coach_id')
    def onchange_tl_appraisal(self):
        if self.appraisal_by_tl and self.coach_id:
            self.appraisal_tl_ids = [self.coach_id.id]
        else:
            self.appraisal_tl_ids = False

 
    @api.onchange('appraisals_by_ro', 'appraisal_by_ro')
    def onchange_ro_appraisal(self):
        if self.appraisals_by_ro and self.appraisal_by_ro:
            self.appraisal_ro_ids = [self.appraisal_by_ro.id]
        else:
            self.appraisal_ro_ids = False

 
# send appraisal button action
 
    @api.multi
    def action_confirm_appraisal(self):
        today_date = datetime.today().strftime('%Y-%m-%d')
        employee_obj = self.env['hr.employee'].search([('id','=',self.id)])
        employee_list = []
        for val in employee_obj:
            if val.appraisal_date:
                date = val.appraisal_date           
                new_date = datetime.strptime(date, '%Y-%m-%d') - timedelta(days=15) 
                new_date = new_date.strftime('%Y-%m-%d')             
                if new_date>=today_date:
                    raise Warning(_('Check next appraisal date'))
            
            emp_id = self.env['hr.appraisal'].create({'employee_id': val.id,          
                                        'name': val,
                                        'date_close': datetime.now(),
                                        'employee_appraisal': val.appraisal_self,
                                        'appraisal_by_tl': val.appraisal_by_tl,
                                        'appraisals_by_ro': val.appraisals_by_ro,
                                        'manager_appraisal': val.appraisal_by_manager,
                                        'appraisals_by_hr': val.appraisals_by_hr,
                                        
                                        'employee_survey_id': val.appraisal_self_survey_id.id,
                                        'manager_survey_id': val.appraisal_manager_survey_id.id,
                                        'appraisal_tl_id': val.appraisal_tl_id.id,
                                        'appraisal_ro_id': val.appraisal_ro_id.id,
                                        'appraisal_hr_id': val.appraisal_hr_id.id,
                                                                               
                                        'appraisal_tl_ids':  [(6, 0, val.appraisal_tl_ids.ids)],
                                        'appraisal_ro_ids':  [(6, 0, val.appraisal_ro_ids.ids)],
                                        'manager_ids':  [(6, 0, val.appraisal_manager_ids.ids)],
                                        'appraisal_hr_ids': [(6, 0, val.appraisal_hr_ids.ids)],                                                                   
                                         })
            employee_list.append(emp_id.id)
            if emp_id:
                tree_id = self.env.ref('hr_appraisal.view_hr_appraisal_tree').id
                form_id = self.env.ref('hr_appraisal.view_hr_appraisal_form').id
                       
        return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'res_model': 'hr.appraisal',
                    'domain': [('id', '=', employee_list)],
                    'view_id': False,
                    'views': [(tree_id, 'tree'),(form_id,'form')],
                    }  
                      

 # hr.appraisal form
   
class HrAppraisal(models.Model):
    _inherit = "hr.appraisal"
    
    appraisal_by_tl = fields.Boolean(string='TL')    
    appraisal_tl_ids = fields.Many2many('hr.employee', 'appraisal_manager_rels', 'hr_appraisal_id')   
    appraisal_tl_id  = fields.Many2one('survey.survey', 'Appraisal Tl')
    
    appraisals_by_ro = fields.Boolean(string='RO')
    appraisal_ro_ids = fields.Many2many('hr.employee', 'appraisal_ro_rel', 'hr_appraisal_id')
    appraisal_ro_id  = fields.Many2one('survey.survey', 'Appraisal Ro')
   
    appraisals_by_hr = fields.Boolean(string='HR')   
    appraisal_hr_ids = fields.Many2many('hr.employee', 'appraisal_hr_rel', 'hr_appraisal_id',domain=[('manager', '=', True)])
    appraisal_hr_id  = fields.Many2one('survey.survey', 'Appraisal Tl')
    
    
    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.appraisal_by_tl = self.employee_id.appraisal_by_tl
            self.appraisal_tl_ids = self.employee_id.appraisal_tl_ids
            self.appraisal_tl_id = self.employee_id.appraisal_tl_id 
                       
            self.appraisals_by_ro = self.employee_id.appraisals_by_ro
            self.appraisal_ro_ids = self.employee_id.appraisal_ro_ids
            self.appraisal_ro_id = self.employee_id.appraisal_ro_id          
             
            self.appraisals_by_hr = self.employee_id.appraisals_by_hr
            self.appraisal_hr_ids = self.employee_id.appraisal_hr_ids
            self.appraisal_hr_id = self.employee_id.appraisal_hr_id          
            
            self.manager_appraisal = self.employee_id.appraisal_by_manager
            self.manager_ids = self.employee_id.appraisal_manager_ids
            self.manager_survey_id = self.employee_id.appraisal_manager_survey_id

            self.appraisals_by_hr = self.employee_id.appraisals_by_hr
            self.appraisal_hr_ids = self.employee_id.appraisal_hr_ids
            self.appraisal_hr_id = self.employee_id.appraisal_hr_id



