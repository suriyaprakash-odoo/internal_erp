# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models, api, _
from datetime import datetime
from odoo.exceptions import ValidationError, UserError
import uuid

class Applicant(models.Model):
    _inherit = "hr.applicant"
    
    applicant_academic_experience_ids = fields.One2many('hr.experience.academics','applicant_academic_id',string="Academic Experience")
    applicant_professional_experience_ids = fields.One2many('hr.experience.professional','applicant_professional_id',string="Professional Experience")
    applicant_certification_experience_ids = fields.One2many('hr.experience.certification','applicant_certification_id',string="Certification Experience")
    state_issued_id = fields.Many2one('res.country.state',"State Issued")
    academic_info_dict = fields.Text("Academic Info Ref")
    professional_info_dict = fields.Text("Professional Info Ref")
    certification_info_dict = fields.Text("Certification Info Ref")
    references_info_dict = fields.Text("References Info Ref")
    
    job_id_country_id = fields.Many2one('res.country',string="Applied Job Country" ,default=lambda self: self.env.user.company_id.country_id.id)
    
    applicant_summary = fields.Text('Applicant Summary')

    access_token = fields.Char(
        'Security Token', copy=False, default=lambda self: str(uuid.uuid4()),
        required=True)
    
    @api.onchange('job_id')
    def onchange_job_id_country_id(self):
        self.job_id_country_id = self.job_id.company_id.country_id
    
    @api.model
    def create(self, vals):
        res=super(Applicant, self).create(vals)
        print(vals)

        if vals.get('partner_phone'):
            if len(vals.get('partner_phone')) != 10:
                raise ValidationError('Please enter valid mobile number')

        if vals.get('partner_mobile'):
            if len(vals.get('partner_mobile')) != 10:
                raise ValidationError('Please enter valid mobile number')

        if vals.get('academic_info_dict'):
            academics_list = []
            for record in eval(vals.get('academic_info_dict')):
                academics_list.append((0,0,{'degree':record[1] or None, 
                    'field_of_study':record[2] or None, 
                    'institute':record[3] or None, 
                    'percentage':record[4] or None, 
                    'year_of_passing':record[5] or None, 
                    }))
            for item in academics_list:
                self.env['hr.experience.academics'].create({
                    'degree':item[2]['degree'],
                    'field_of_study':item[2]['field_of_study'],
                    'institute':item[2]['institute'],
                    'percentage':item[2]['percentage'],
                    'year_of_passing':item[2]['year_of_passing'],
                    'applicant_academic_id':res.id
                    })

        if vals.get('professional_info_dict'):
            professional_list = []
            for record in eval(vals.get('professional_info_dict')):
                start_date = end_date = ''
                if record[3]:
                    start_date = datetime.strptime(record[3], '%d-%m-%Y').strftime('%Y/%m/%d')
                if record[4]:
                    end_date = datetime.strptime(record[4], '%d-%m-%Y').strftime('%Y/%m/%d')
                professional_list.append((0,0,{'position':record[1] or None, 
                    'organization':record[2] or None, 
                    'start_date':start_date or None, 
                    'end_date':end_date or None}))
            for item in professional_list:
                self.env['hr.experience.professional'].create({
                    'position':item[2]['position'],
                    'organization':item[2]['organization'],
                    'start_date':item[2]['start_date'],
                    'end_date':item[2]['end_date'],
                    'applicant_professional_id':res.id
                    })
                
        if vals.get('certification_info_dict'):
            certification_list = []
            for record in eval(vals.get('certification_info_dict')):
                start_date = end_date = ''
                if record[4]:
                    start_date = datetime.strptime(record[4],'%d-%m-%Y').strftime('%Y/%m/%d')
                if record[5]:
                    end_date = datetime.strptime(record[5],'%d-%m-%Y').strftime('%Y/%m/%d')
                certification_list.append((0,0,{'certifications':record[1] or None, 
                    'issued_by':record[2] or None, 
                    'state_issued':record[3] or None, 
                    'start_date':start_date or None, 
                    'end_date':end_date or None}))
            for item in certification_list:
                self.env['hr.experience.certification'].create({
                    'certifications':item[2]['certifications'],
                    'issued_by':item[2]['issued_by'],
                    'state_issued_id':item[2]['state_issued'],
                    'start_date':item[2]['start_date'],
                    'end_date':item[2]['end_date'],
                    'applicant_certification_id':res.id,
                    })
        
        if vals.get('references_info_dict'):
            reference_list = []
            for record in eval(vals.get('references_info_dict')):
                reference_list.append((0,0,{'name':record[1] or None, 
                    'relationship':record[2] or None, 
                    'no_years':record[3] or None, 
                    'occupation':record[4] or None, 
                    'annual_income':record[5] or None, 
                    'phone_number':record[6] or None, 
                    }))
            for item in reference_list:
                self.env['applicant.reference.details'].create({
                    'name':item[2]['name'],
                    'relationship_app':item[2]['relationship'],
                    'no_years':item[2]['no_years'],
                    'occupation':item[2]['occupation'],
                    'address_details':item[2]['annual_income'],
                    'phone_no':item[2]['phone_number'],
                    'applicant_reference_id':res.id
                    })

        return res  


    @api.multi
    def write(self, vals):
        # user_id change: update date_open
        
        res = super(Applicant, self).write(vals)

        if vals.get('partner_phone'):
            if len(vals.get('partner_phone')) != 10:
                raise ValidationError('Please enter valid mobile number')

        if vals.get('partner_mobile'):
            if len(vals.get('partner_mobile')) != 10:
                raise ValidationError('Please enter valid mobile number')

        return res
    
class AcademicExperiences(models.Model):
    _inherit = "hr.experience.academics"
    
    applicant_academic_id = fields.Many2one('hr.applicant',string="Applicant Academic")
    
class ProfessionalExperiences(models.Model):
    _inherit = "hr.experience.professional"
    
    applicant_professional_id = fields.Many2one('hr.applicant',string="Applicant Professional")
    
class CertificationDetail(models.Model):
    _inherit = "hr.experience.certification"
    
    applicant_certification_id = fields.Many2one('hr.applicant',string="Applicant Certification")
    
    