from odoo import api, fields, models,_

    
class AcademicExperiences(models.Model):
    _name = "hr.experience.academics"
#     _rec_name = "employee"
    
    employee = fields.Many2one('hr.employee',string="Employee")
    course = fields.Char("Course", required=True)
    degree = fields.Char("Degree")
    major = fields.Char("Major")
    year_from = fields.Char("From")
    year_to = fields.Char("To")
    percentage = fields.Char("Percentage")
    institute = fields.Char("Institution")
    location = fields.Char("Location")
    
    year_of_passing = fields.Char("Year of Passing")
    field_of_study = fields.Char("Field of Study")
#     academic_experience_id = fields.Many2one('hr.employee', string="Academic Experience Ref")


class ProfessionalExperiences(models.Model):
    _name = "hr.experience.professional"
#     _rec_name = "employee"
    
    employee = fields.Many2one('hr.employee',string="Employee")
    position = fields.Char("Designation", required=True)
    organization = fields.Char("Organisation/Place")
    start_date = fields.Date("From Month")
    end_date = fields.Date("To Month")
    tenure = fields.Char('Tenure(Months)')
    salary = fields.Float("Salary/Month")
    change_reason = fields.Char("Reason for Change")
#     professional_experience_id = fields.Many2one('hr.employee', string="Professional Experience Ref")


class CertificationDetail(models.Model):
    _name = "hr.experience.certification"
#     _rec_name = "employee"
    
    employee = fields.Many2one('hr.employee',string="Employee")
    certifications = fields.Char("Certifications", required=True)
#     certification_number = fields.Char("Certification #")
    issued_by = fields.Char("Issued By")
#     professional_license = fields.Boolean("Professional License")
    country_id = fields.Many2one('res.country',"Applied Job Country")
    state_issued_id = fields.Many2one('res.country.state',"State Issued")
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
#     certification_id = fields.Many2one('hr.employee', string="Certification Ref")
    
    
