from odoo import fields, models, api, _
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    trial_date_start = fields.Date("Start of Trial Date ",track_visibility='onchange')
    job_seniority_id = fields.Many2one('hr.job.seniority.title',string="Job seniority title")
    benefits_epf = fields.Boolean(string="EPF")
    benefits_esi = fields.Boolean(string="ESI")
    benefits_medical_policy = fields.Boolean(string="Medical Policy")
    basic_salary = fields.Float(string="Basic")
    special_allowance = fields.Float(string="Special Allowance")
    rent_allowance = fields.Float(string="House Rent Allowance (HRA)")
    project_allowance = fields.Float(string="Project Allowance")
    transport = fields.Float(string="Transport")
    exgratia = fields.Float(string="Exgratia")
    medical_allowance = fields.Float(string="Medical Allowance")
    gross_salary = fields.Float(string="Gross")
    mediclaim = fields.Float(string="Mediclaim")
    
    @api.onchange("gross_salary")
    def gross_salary_onchange(self):
        rule_id = False
        if self.gross_salary:
            if self.employee_type:
                rule_id = self.env['hr.contract.rule'].search([('from_amount','<=', self.gross_salary),('to_amount','>=', self.gross_salary),('employee_type','=',self.employee_type)], limit=1)
            else:
                rule_id = self.env['hr.contract.rule'].search([('from_amount','<=', self.gross_salary),('to_amount','>=', self.gross_salary)], limit=1)
            if rule_id:
                if rule_id.basic:
                    if rule_id.basic_method == 'percent':
                        self.basic_salary = ((self.gross_salary*rule_id.basic)/100)
                    elif rule_id.basic_method == 'fixed':
                        self.basic_salary = rule_id.basic
                    else:
                        self.basic_salary = 0 
                else:
                    self.basic_salary = 0
                    
                if rule_id.hra:
                    if rule_id.hra_method == 'percent':
                        self.rent_allowance = ((self.basic_salary*rule_id.hra)/100)
                    elif rule_id.hra_method == 'fixed':
                        self.rent_allowance = rule_id.hra
                    else:
                        self.rent_allowance = 0 
                else:
                    self.rent_allowance = 0
                    
                if rule_id.transport:
                    if rule_id.transport_method == 'percent':
                        self.transport = ((self.basic_salary*rule_id.transport)/100)
                    elif rule_id.transport_method == 'fixed':
                        self.transport = rule_id.transport
                    else:
                        self.transport = 0 
                else:
                    self.transport = 0
                    
                if rule_id.medical:
                    if rule_id.medical_method == 'percent':
                        self.medical_allowance = ((self.basic_salary*rule_id.medical)/100)
                    elif rule_id.medical_method == 'fixed':
                        self.medical_allowance = rule_id.medical
                    else:
                        self.medical_allowance = 0 
                else:
                    self.medical_allowance = 0
                    
                if self.gross_salary:
                    self.special_allowance = abs(self.gross_salary-self.basic_salary-self.rent_allowance-self.transport-self.medical_allowance)
                else:
                    self.special_allowance = 0
                    
                if rule_id.project:
                    if rule_id.project_method == 'percent':
                        self.project_allowance = ((self.basic_salary*rule_id.project)/100)
                    elif rule_id.project_method == 'fixed':
                        self.project_allowance = rule_id.project
                    else:
                        self.project_allowance = 0 
#                     self.project_allowance = rule_id.project
                else:
                    self.project_allowance = 0
                    
                if rule_id.exgratia:
                    if rule_id.exgratia_method == 'percent':
                        self.exgratia = ((self.basic_salary*rule_id.exgratia)/100)
                    elif rule_id.exgratia_method == 'fixed':
                        self.exgratia = rule_id.exgratia
                    else:
                        self.exgratia = 0 
                else:
                    self.exgratia = 0
                    
            else:
                self.basic_salary = 0
                self.rent_allowance = 0
                self.transport = 0
                self.medical_allowance = 0
                self.special_allowance = 0
                self.project_allowance = 0
                self.exgratia = 0
        else:
                self.basic_salary = 0
                self.rent_allowance = 0
                self.transport = 0
                self.medical_allowance = 0
                self.special_allowance = 0
                self.project_allowance = 0
                self.exgratia = 0
                
