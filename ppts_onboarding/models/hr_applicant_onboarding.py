from odoo import fields, models, api, _

class Applicant(models.Model):
    _inherit = "hr.applicant"

    @api.multi
    def write(self, vals):
        stage_obj = self.env['hr.recruitment.stage'].search([('name', '=', 'Onboarding')])
        
        if vals.get('stage_id') == stage_obj.id:
            onboarding_id=self.env['hr.employee.onboarding'].search([('applicant_id', '=', self.id)])
            if not onboarding_id:
                onboard_id = self.env['hr.employee.onboarding'].create({
                    'name' : self.name or False,
                    'firstname' : self.partner_name or False,
                    'middlename' : self.middlename or False,
                    'lastname' : self.lastname or False,
                    'mail' : self.email_from or False,
                    'phone' : self.partner_phone or False,
                    'responsible' : self.user_id.id or False,
                    'applied_job' : self.job_id.id or False,
                    'company' : self.company_id.id or False,
                    'applicant_id' : self.id,
                    'state_id' : 'offer',
                    'expected_salary' : self.salary_expected,
                    'proposed_salary' : self.salary_proposed,
                    'available' : self.availability,
                    'priority' : self.priority,
                    'marital_status' : self.status_type,
                    'gender':self.gender,
                    'dob':self.date_birth,
                    'age':self.age,
                    'available':self.availability,
                    'street' : self.applicant_street,
                    'street2': self.p_resi,
                    'city' : self.p_city,
                    'state' : self.permanent_state.id,
                    'zip' : self.p_pin,
                    'country' : self.p_country.id,
                    'contract_type' : self.job_id.job_type.id,
                })
                
                for line in self.applicant_academic_experience_ids:
                    for values in line:
                        self.env['hr.experience.academics'].create({
                            'degree':values.degree,
                            'institute':values.institute,
                            'field_of_study':values.field_of_study,
                            'percentage':values.percentage,
                            'year_of_passing':values.year_of_passing,
                            'employee_academic_id':onboard_id.id,
                            }) 
                for line in self.applicant_professional_experience_ids:
                    for values in line:
                        self.env['hr.experience.professional'].create({
                            'position':values.position,
                            'organization':values.organization,
                            'start_date':values.start_date,
                            'end_date':values.end_date,
                            'employee_professional_id':onboard_id.id,
                            }) 
                for line in self.applicant_certification_experience_ids:
                    for values in line:
                        self.env['hr.experience.certification'].create({
                            'certifications':values.certifications,
                            'issued_by':values.issued_by,
                            'state_issued_id':values.state_issued_id.id,
                            'start_date':values.start_date,
                            'end_date':values.end_date,
                            'employee_certification_id':onboard_id.id,
                            }) 
            
            partner = self.env['res.partner'].search([('applicant_id','=',self.id)])
            if not partner:
                applicant_name = str(self.partner_name or '') + ' ' + str(self.middlename or '') + ' ' + str(self.lastname or '')
                partner = self.env['res.partner'].create({'name':applicant_name or '',
                                                          'partner_name':applicant_name or '',
                                                          'email':self.email_from or '',
                                                          'phone':self.partner_phone or '',
                                                          'function':self.job_id.name or '',
                                                          'applicant_id':self.id or '',
                                                          'mobile':self.partner_mobile or ''
                                                        }) 
                onboard_id.partner_id = partner.id       
            else:
                onboarding_id.partner_id = partner.id

        res = super(Applicant, self).write(vals)
        return res

class ResPartner(models.Model):
    _inherit = "res.partner"   
     
    applicant_id = fields.Many2one("hr.applicant",string="Applicant")
                
