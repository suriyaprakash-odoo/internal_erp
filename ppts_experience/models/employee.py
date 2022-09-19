from odoo import fields, models, api, _


class Employee(models.Model):
    _inherit = "hr.employee"
    
    employee_academic_experience_ids = fields.One2many('hr.experience.academics','employee_exp_academic_id',string="Academic Experience")
    fresher = fields.Boolean('Fresher')
    employee_professional_experience_ids = fields.One2many('hr.experience.professional','employee_exp_professional_id',string="Professional Experience")
    employee_certification_experience_ids = fields.One2many('hr.experience.certification','employee_exp_certification_id',string="Certification Experience")
    state_issued_id = fields.Many2one('res.country.state',"State Issued")
    
    job_country_id = fields.Many2one("res.country",string="Applied Job Country")

    @api.onchange('job_id')
    def onchange_job_country_id(self):
        self.job_country_id = self.job_id.company_id.country_id

class AcademicExperiences(models.Model):
    _inherit = "hr.experience.academics"
    
    employee_exp_academic_id = fields.Many2one('hr.employee',string="Applicant Academic")
    
class ProfessionalExperiences(models.Model):
    _inherit = "hr.experience.professional"
    
    employee_exp_professional_id = fields.Many2one('hr.employee',string="Applicant Professional")
    
class CertificationDetail(models.Model):
    _inherit = "hr.experience.certification"
    
    employee_exp_certification_id = fields.Many2one('hr.employee',string="Applicant Certification")
    
    