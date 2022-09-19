from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from docutils.nodes import Bibliographic
import re
import datetime
from datetime import datetime, timedelta
import uuid
from urllib.parse import urljoin
from odoo.addons.http_routing.models.ir_http import slug

class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    onboarding_id = fields.Many2one('hr.employee.onboarding', string='Onboarding')

    @api.model
    def create(self, vals):
        ctx = self.env.context
        if ctx.get('active_id') and ctx.get('active_model') == 'hr.employee.onboarding':
            vals['onboarding_id'] = ctx.get('active_id')
        return super(SurveyUserInput, self).create(vals)

    @api.multi
    def write(self,vals):
        if vals.get('state'):
            if vals['state']=='done':
                if self.onboarding_id:
                    self.onboarding_id.benefits_states = 'complete'

        return super(SurveyUserInput, self).write(vals)


class HrOnboarding(models.Model):
    _name = "hr.employee.onboarding"
    _inherit = ['mail.thread']
    
    name = fields.Char("Name", track_visibility='onchange')
    firstname = fields.Char("First Name", track_visibility='onchange')
    middlename = fields.Char("Middle Name", track_visibility='onchange')
    lastname = fields.Char("Last Name", track_visibility='onchange')
    phone = fields.Char("Phone", track_visibility='onchange')
    mail = fields.Char("Email", track_visibility='onchange')
    applied_job = fields.Many2one('hr.job', string="Applied Job", track_visibility='onchange')
    applicant_id = fields.Char("Applicant ID", readonly=True, track_visibility='onchange')
    start_date = fields.Date("Start Date", default=fields.datetime.now(), track_visibility='onchange')
    company = fields.Many2one('res.company', string="Company", track_visibility='onchange')
    responsible = fields.Many2one('res.users', string="Responsible", track_visibility='onchange')
    emp_status = fields.Many2one('hr.contract.type', string="Employee Status", track_visibility='onchange')
    expected_salary = fields.Char("Expected Salary", track_visibility='onchange')
    proposed_salary = fields.Char("Proposed Salary", track_visibility='onchange')
    available = fields.Date("Availability", track_visibility='onchange')
    pay_type = fields.Selection([('yearly', 'Annual Wage'),
                                 ('monthly', 'Monthly Wage'),
                                 ('hourly', 'Hourly Wage')], string="Pay Type", track_visibility='onchange')
    state_id = fields.Selection([('offer', 'Offer Accepted'),
                                 ('background', 'Background Check'),
                                 ('to_approve', 'To Approve'),
                                 ('contract', 'Contract'),
                                 ('complete', 'Complete'),
                                 ('reject', 'Rejected')], string="Status", default='offer', track_visibility='onchange')
    contract_type = fields.Many2one('hr.contract.type', string="Contract Type")
    substate_id = fields.Selection([('started', 'GetStarted0'),
                                 ('personal', 'PersonalInformation1'),
                                 ('experience', 'ExperienceandCertifications2'),
                                 ('medical', 'MedicalInformation3'),
                                 ('employement', 'EmployementInformation4'),
                                 ('offer_summary', 'Summary5'),
                                 ('bgv','BackgroundVerification6'),
                                 ('background_check', 'BackgroundCheck7'),
                                 ('document_check', 'DocumentCheck8'),
                                 ('summary_8', 'Summary9'),
                                 ('app_summary', 'ApplicantSummary/Hire10'),
                                 ('ben_eligiblity', 'BenefitsEligibility11'),
                                 ('welcome', 'WelcomeEmail12'),
                                 ('on_boardingchecklist', 'OnboardingChecklist13'),
                                 ('appraisal', 'AppraisalPlan14'),
                                 ('employee_summary', 'EmployeeSummary15'),
                                 ('create_contract', 'CreateContract16'),
                                 ('contract_summary', 'ContractSummary17'),
                                 ('completed', 'Complete18')], string="Onboarding Status", default='started')
    priority = fields.Selection([('0', 'Normal'),
                               ('1', 'Good'),
                               ('2', 'Very Good'),
                               ('3', 'Excellent')], "Appreciation", default='0')
    benefits_states = fields.Selection([('pending', 'Pending'),
                                    ('progress', 'In Progress'),
                                    ('complete', 'Completed')],default='pending', string="Benefit Status")
    benefits_survey_link = fields.Char("Benefits Survey URL")
    pid_document_id = fields.Many2one('signature.request', string="PID Document")
    partner_id = fields.Many2one('res.partner')
    id_number = fields.Char("Identification Number", track_visibility='onchange')
    progress_percentage = fields.Integer(compute="_compute_progress_percentage")
    first_name_alias = fields.Char("First Name", track_visibility='onchange')
    middle_name_alias = fields.Char("Middle Name", track_visibility='onchange')
    last_name_alias = fields.Char("Last Name", track_visibility='onchange')
    emergency_contact_name = fields.Char("Name")
    emergency_contact_phone = fields.Char("Phone")
    emergency_contact_relationship = fields.Char("Relationship")
    nationality = fields.Many2one('res.country', string="Nationality", track_visibility='onchange')
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female')], string="Gender", track_visibility='onchange')
    marital_status = fields.Selection([('single', 'Single'),
                                       ('married', 'Married'),
                                       ('widower', 'Widower'),
                                       ('divorced', 'Divorced')], string="Marital Status", track_visibility='onchange')
    street = fields.Char("Home Address", track_visibility='onchange')
    street2 = fields.Char(track_visibility='onchange')
    city = fields.Char(track_visibility='onchange')
    state = fields.Many2one("res.country.state", domain="[('country_id','=',country)]", string='State', track_visibility='onchange', ondelete='restrict')
    country = fields.Many2one('res.country', string='Country', track_visibility='onchange', ondelete='restrict')
    zip = fields.Char(track_visibility='onchange')
#     no_of_children = fields.Char("Number of Allowances",track_visibility='onchange')
    passport_number = fields.Char("Passport Number", track_visibility='onchange')
    dl_number = fields.Char("Driving License Number", track_visibility='onchange')
    dob = fields.Date("Date of Birth", track_visibility='onchange')
    birth_country = fields.Many2one('res.country', string="Birth Country", track_visibility='onchange')
    place_of_birth = fields.Char("Place of Birth", track_visibility='onchange')
    age = fields.Integer("Age", track_visibility='onchange')
#     ethnic_id = fields.Char("Ethnic ID",track_visibility='onchange')
#     smoker = fields.Char("Smoker",track_visibility='onchange')
    notes = fields.Text("Notes")
    academic_experience_ids = fields.One2many('hr.experience.academics', 'employee_academic_id', string="Academic Experience")
    professional_experience_ids = fields.One2many('hr.experience.professional', 'employee_professional_id', string="Professional Experience")
    certification_ids = fields.One2many('hr.experience.certification', 'employee_certification_id', string="Certifications")
    bgv_info_ids = fields.One2many('background.verification', 'bgv_info_id', string="BGV Info")
#     applicant_background_ids = fields.One2many('applicant.background', 'applicant_background_id', string="Applicant")
    vision = fields.Char('Vision')
    chronic = fields.Char(string="Chronic Illness(Long term illness like wheezing,asthma, diabetes, allergies etc.,)")
    undergone = fields.Char(string="Undergone any surgery in the past or met with an accident ")
    cardiac = fields.Char(string="Cardiac")
    frequent = fields.Char(string="Frequent headaches,migraine, back pain etc")
    others = fields.Char(string="Any others in specific")
    job_seniority_title = fields.Many2one('hr.job.seniority.title', string="Job Seniority Title", track_visibility='onchange')
    emp_start_date = fields.Date("Start Date", track_visibility='onchange')
    scheduled_hours = fields.Integer("Scheduled Hours", track_visibility='onchange')
#     benifits_seniority_date = fields.Date("Benefits Seniority Date",track_visibility='onchange')
    pay_rate = fields.Float("Pay Rate", track_visibility='onchange')
    employee_id = fields.Many2one("hr.employee", string="Employee") 
    tenure = fields.Char("Tenure")
    cost_of_comapny = fields.Char("Cost to Company")
    reporting_manger_name = fields.Char("Reporting Manager Name")
    reporting_manger_designation = fields.Char("Reporting Manager Designation")
    reason_leaving = fields.Char("Reason for leaving")
    attached_document = fields.Char("Attached Document  - Genuine / Not Genuine")
    feedback_on_account = fields.Char("Feedback on account of Disciplinary/Ethical/Integrity conduct on the job")
    source_of_verification = fields.Char("Source of Verification")
    exit_formalities = fields.Char("Exit Formalities Completed ")
    designation = fields.Char("Designation")
    employee_code = fields.Char("Employee Code")
    reporting_manger_email_id = fields.Char("Reporting Manager Email ID")
    reporting_manger_tele_no = fields.Char("Reporting Manager Tele No")
    eligibility_for_rehire = fields.Char("Eligibility for rehire& Reasons")
    referee_details = fields.Char("Referee's Details")
    date_and_time = fields.Datetime("Date and Time")
    notice_period = fields.Char("Notice Period Completed")
    any_other_commands = fields.Char("Any other comments: (Please Specify)")
    benefits_epf = fields.Boolean("EPF")
    benefits_esi = fields.Boolean("ESI")
    benefits_medical_policy = fields.Boolean("Medical Policy")
    new_contract_id = fields.Many2one('hr.contract', string="Contract ID")
    aadhar_card = fields.Selection([('yes', 'Yes'), ('no', 'No')], "Aadhar Card")
    tenth_marksheet = fields.Selection([('yes', 'Yes'), ('no', 'No')], "10th Marksheet")
    voter_id = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Voter Id')
    twelveth_marksheet = fields.Selection([('yes', 'Yes'), ('no', 'No')], "12th Marksheet")
    college_marksheet = fields.Selection([('yes', 'Yes'), ('no', 'No')], "College Marksheet")
    tc = fields.Selection([('yes', 'Yes'), ('no', 'No')], "TC")
#     attached_document = fields.Binary("Attachement")
    
    pf = fields.Char("PF")
    esino = fields.Char("ESI No")
    aadhaar = fields.Char("Aadhar")
    pan = fields.Char("PAN")
    image = fields.Binary("Image")
    on_nda = fields.Boolean("NDA")
    on_employeemanual = fields.Boolean("Employee manual")
    image = fields.Binary("Photo", attachment=True,
        help="This field holds the image used as photo for the employee, limited to 1024x1024px.")

    
    
    def _compute_progress_percentage(self):
        if self.substate_id == 'started':
            self.progress_percentage = 0
        if self.substate_id == 'personal':
            self.progress_percentage = 5
        if self.substate_id == 'experience':
            self.progress_percentage = 10
        if self.substate_id == 'medical':
            self.progress_percentage = 15    
        if self.substate_id == 'employement':
            self.progress_percentage = 20
        if self.substate_id == 'offer_summary':
            self.progress_percentage = 25
        if self.substate_id == 'bgv':
            self.progress_percentage = 30
        if self.substate_id == 'background_check':
            self.progress_percentage = 35
        if self.substate_id == 'document_check':
            self.progress_percentage = 40
        if self.substate_id == 'summary_8':
            self.progress_percentage = 45
        if self.substate_id == 'app_summary':
            self.progress_percentage = 50
        if self.substate_id == 'ben_eligiblity':
            self.progress_percentage = 55
        if self.substate_id == 'welcome':
            self.progress_percentage = 60
        if self.substate_id == 'on_boardingchecklist':
            self.progress_percentage = 65
        if self.substate_id == 'appraisal':
            self.progress_percentage = 70
        if self.substate_id == 'employee_summary':
            self.progress_percentage = 75
        if self.substate_id == 'create_contract':
            self.progress_percentage = 80
        if self.substate_id == 'contract_summary':
            self.progress_percentage = 90
        if self.substate_id == 'completed':
            self.progress_percentage = 100
            
    def get_started_info(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        con_type = self.env['hr.contract.type'].sudo().search([])
        contract_types_dict = {}
        for lines in con_type:
            contract_types_dict.update({lines.id:lines.name})
        get_started_dict = {
                'name' : vals.name or '',
                'mail' : vals.mail or '',
                'phone' : vals.phone or '',
                'responsible' : vals.responsible.name or '',
                'applied_job' : vals.applied_job.name or '',
                'company' : vals.company.name or '',
                'applicant_id' : vals.applicant_id,
                'expected_salary': vals.expected_salary or 0.00,
                'proposed_salary' : vals.proposed_salary or 0.00,
                'available' : vals.available or '',
                'contract_type' : vals.contract_type.id or '',
                'pay_type' : vals.pay_type or '',
                'contract_type_disp' : contract_types_dict,
                'priority' : vals.priority,
                'score' : 0.00,
                } 
        return get_started_dict
    
    def change_state_name(self, country_id):
        country_obj = self.env['res.country.state'].search([('country_id.id' , '=' , country_id)])
        state_dict = {}
        for lines in country_obj:
            state_dict.update({lines.id:lines.name})

        return state_dict
    
    def insert_records_get_started(self, form_id, get_started, from_pid=None):
        get_started_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if get_started['con_typ']:
            get_started_obj.contract_type = int(get_started['con_typ'])
            get_started_obj.emp_status = int(get_started['con_typ'])
        if get_started['pay_typ']:
            get_started_obj.pay_type = get_started['pay_typ']

        if not get_started_obj.pid_document_id:
            return get_started_obj.substate_id

        else:
            if get_started_obj.substate_id == 'started':
                get_started_obj.substate_id = 'personal'
                
    def personalinfo(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        country = self.env['res.country'].sudo().search([])
        country_dict = {}
        for lines in country:
            country_dict.update({lines.id:lines.name})
        state = self.env['res.country.state'].sudo().search([])
        state_dict = {}
        for lines in state:
            state_dict.update({lines.id:lines.name})
        personal_info_dict = {
                'id_no' : vals.id_number or '',
                'passport_no' : vals.passport_number or '',
                'dl_no' : vals.dl_number or '',
                'street' : vals.street or '',
                'street2' : vals.street2 or '',
                'city' : vals.city or '',
                'state' : int(vals.state.id) or '',
                'country_id' : vals.country.id or '',
                'zip' : vals.zip or '',
                'first_name_alias' : vals.first_name_alias or '',
                'middle_name_alias' : vals.middle_name_alias or '',
                'last_name_alias' : vals.last_name_alias or '',
                'emergency_contact_name' : vals.emergency_contact_name or '',
                'emergency_contact_phone' : vals.emergency_contact_phone or '',
                'emergency_contact_relationship' : vals.emergency_contact_relationship or '',
                'gender' : vals.gender or '',
                'place_of_birth' : vals.place_of_birth or '',
                'nationality' : vals.nationality.id or '',
                'birth_country' : vals.birth_country.id or '',
                'marital_status': vals.marital_status or '',
#                 'children' : vals.no_of_children or '',
#                 'ethnic_id' : vals.ethnic_id or '',
#                 'smoker' : vals.smoker or '',
                'dob' : vals.dob or '',
                'age' : vals.age or '',
                'country' : country_dict,
                'state_dict' : state_dict,
            }
        
        return personal_info_dict     
    
    def insert_records_personal_info(self, form_id, personal_info):
        personal_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if (personal_info['id_no']):
            personal_info_obj.id_number = personal_info['id_no']
        if (personal_info['passport_no']):
            personal_info_obj.passport_number = personal_info['passport_no']
        if (personal_info['dl_no']):
            personal_info_obj.dl_number = personal_info['dl_no']
        if (personal_info['street']):
            personal_info_obj.street = personal_info['street']
        if (personal_info['street2']):
            personal_info_obj.street2 = personal_info['street2']
        if (personal_info['city']):
            personal_info_obj.city = personal_info['city']
        if (personal_info['state']):
            personal_info_obj.state = int(personal_info['state'])
        if (personal_info['country']):
            personal_info_obj.country = int(personal_info['country'])
        if (personal_info['zip']):
            personal_info_obj.zip = personal_info['zip']
#         if (personal_info['fst_name_alias']):
#             personal_info_obj.first_name_alias = personal_info['fst_name_alias']
#         if (personal_info['mid_name_alias']):
#             personal_info_obj.middle_name_alias = personal_info['mid_name_alias']
#         if (personal_info['lst_name_alias']):
#             personal_info_obj.last_name_alias = personal_info['lst_name_alias']
        if (personal_info['emergency_contact_name']):
            personal_info_obj.emergency_contact_name = personal_info['emergency_contact_name']
        if (personal_info['emergency_contact_phone']):
            personal_info_obj.emergency_contact_phone = personal_info['emergency_contact_phone']
        if (personal_info['emergency_contact_relationship']):
            personal_info_obj.emergency_contact_relationship = personal_info['emergency_contact_relationship']
        if (personal_info['gender']):
            personal_info_obj.gender = personal_info['gender']
        if (personal_info['place_of_birth']):
            personal_info_obj.place_of_birth = personal_info['place_of_birth']
        if (personal_info['marital_sts']):
            personal_info_obj.marital_status = personal_info['marital_sts']
#         if (personal_info['noc']):
#             personal_info_obj.no_of_children = personal_info['noc']
#         if (personal_info['ethnic']):
#             personal_info_obj.ethnic_id = personal_info['ethnic']
        if (personal_info['nationality']):
            personal_info_obj.nationality = int(personal_info['nationality'])
        if (personal_info['birth_country']):
            personal_info_obj.birth_country = int(personal_info['birth_country'])
#         if (personal_info['smoker']):
#             personal_info_obj.smoker = personal_info['smoker']
        if (personal_info['age']):
            personal_info_obj.age = personal_info['age']
        if (personal_info['dob']):
            personal_info_obj.dob = personal_info['dob']

        print(personal_info)
        lst = str(personal_info['image']).split(',')
        self.env['ir.attachment'].create({
                                            'res_id':int(form_id),
                                            'res_model':'hr.employee.onboarding',
                                            'index_content':'image',
                                            'type':'binary',
                                            'db_datas':lst[1],
                                            'res_field':'image',
                                            'name':'image',
            })

        if personal_info_obj.substate_id == 'personal':
            personal_info_obj.substate_id = 'experience'

        return personal_info_obj.substate_id   
    
    def remove_record(self, form_id, tree_id, current_model):
        if tree_id:
            remove_obj = self.env[current_model].search([('id', '=', tree_id)])
#             if current_model=='background.check.package':
#                 if remove_obj:
#                     for rec in remove_obj.item.services:
#                         check_id=self.env['background.check'].search([('item','=',rec.id),('background_check_id','=',int(form_id))], limit=1)
#                         if check_id:
#                             check_id.unlink()
#  
#                  
#             download=self.env['background.check.download'].search([('item','=',remove_obj.item.id),('background_check_download_id','=',int(form_id))], limit=1)
#             if download:
#                 download.unlink()
            remove_obj.unlink()
        res = 1    
        return res    
        
    def experienceinfo(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])

        state = self.env['res.country.state'].sudo().search([('country_id' , '=' , vals.applied_job.company_id.country_id.id)])
        
        state_dict = {}
        for lines in state:
            state_dict.update({lines.id:lines.name})
        exp_academic_list = []
        for line in vals.academic_experience_ids:
            exp_academic_list.append({
                'form_academic_exp_tree_id' : line.id or '',
                'academic_experience' : line.degree or '',
                'institute' : line.institute or '',
                'field_of_study' : line.field_of_study or '',
                'percentage' : line.percentage or '',
                'year_of_passing' : line.year_of_passing or '',
                
            })
            
        exp_professional_list = []
        for line in vals.professional_experience_ids:
            exp_professional_list.append({
                'form_professional_exp_tree_id' : line.id or '',
                'position' : line.position or '',
                'organization' : line.organization or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        exp_certificate_list = []
        for line in vals.certification_ids:
            exp_certificate_list.append({
                'form_certification_exp_tree_id' : line.id or '',
                'certifications' : line.certifications or '',
#                  'certificate_code' : line.certificate_code or '',
                'issued_by' : line.issued_by or '',
#                 'professional_license' : line.professional_license or '',
                'state_issued_id' : line.state_issued_id.id or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
        
        experience_info_dict = {
                'exp_academic_list' : exp_academic_list or '',
                'exp_professional_list' : exp_professional_list or '',
                'exp_certificate_list' : exp_certificate_list or '',
                'state_dict' : state_dict or '',
            }
    
        return experience_info_dict    
    
    def insert_records_experience_academic_info(self, form_id, offer_accepted_academic_info):
        if int(offer_accepted_academic_info['academic_tree_id']) > 0:
            academic_info_obj = self.env['hr.experience.academics'].search([('id' , '=' , offer_accepted_academic_info['academic_tree_id'])])
            if (offer_accepted_academic_info['academic_exp']):
                academic_info_obj.degree = offer_accepted_academic_info['academic_exp']
            if (offer_accepted_academic_info['academic_institution']):
                academic_info_obj.institute = offer_accepted_academic_info['academic_institution']
            if (offer_accepted_academic_info['academic_fos']):
                academic_info_obj.field_of_study = offer_accepted_academic_info['academic_fos']
            if (offer_accepted_academic_info['academic_passing']):
                academic_info_obj.year_passing = offer_accepted_academic_info['academic_passing']
            if (offer_accepted_academic_info['academic_percentage']):
                academic_info_obj.year_of_passing = offer_accepted_academic_info['academic_percentage']        
                 
        else:
            if (offer_accepted_academic_info['academic_exp'] or offer_accepted_academic_info['academic_institution']):
                academic_info_obj = self.env['hr.experience.academics'].create({
                    'degree' : offer_accepted_academic_info['academic_exp'],
                    'institute' : offer_accepted_academic_info['academic_institution'],
                    'field_of_study' : offer_accepted_academic_info['academic_fos'] or '',
                    'year_of_passing' : offer_accepted_academic_info['academic_passing'] or '',
                    'percentage' : offer_accepted_academic_info['academic_percentage'] or '',
                    'employee_academic_id':form_id
                    })   
    
    def insert_records_experience_professional_info(self, form_id, offer_accepted_professional_info):
        if int(offer_accepted_professional_info['professional_tree_id']) > 0:
            professional_info_obj = self.env['hr.experience.professional'].search([('id' , '=' , offer_accepted_professional_info['professional_tree_id'])])
            if (offer_accepted_professional_info['position']):
                professional_info_obj.academic_experience = offer_accepted_professional_info['position']
            if (offer_accepted_professional_info['organization']):
                professional_info_obj.institute = offer_accepted_professional_info['organization']
            if (offer_accepted_professional_info['professional_start']):
                professional_info_obj.start_date = offer_accepted_professional_info['professional_start']
            if (offer_accepted_professional_info['professional_end']):
                professional_info_obj.end_date = offer_accepted_professional_info['professional_end']       
                 
        else:
            if (offer_accepted_professional_info['position'] or offer_accepted_professional_info['organization']):
                professional_info_obj = self.env['hr.experience.professional'].create({
                    'position' : offer_accepted_professional_info['position'],
                    'organization' : offer_accepted_professional_info['organization'],
                    'start_date' : offer_accepted_professional_info['professional_start'] or False,
                    'end_date' : offer_accepted_professional_info['professional_end'] or False,
                    'employee_professional_id':form_id
                    })    
    
    def insert_records_experience_certification_info(self, form_id, offer_accepted_certificate_info):
        if int(offer_accepted_certificate_info['certificate_tree_id']) > 0:
            certification_info_obj = self.env['hr.experience.certification'].search([('id' , '=' , offer_accepted_certificate_info['certificate_tree_id'])])
            if (offer_accepted_certificate_info['certificate']):
                certification_info_obj.academic_experience = offer_accepted_certificate_info['certificate']
#             if (offer_accepted_certificate_info['certificate_no']):
#                 certification_info_obj.institute = offer_accepted_certificate_info['certificate_no']
            if (offer_accepted_certificate_info['issued_by']):
                certification_info_obj.diploma = offer_accepted_certificate_info['issued_by']
            if (offer_accepted_certificate_info['state_issued_id']):
                certification_info_obj.state_issued_id = offer_accepted_certificate_info['state_issued_id']
            if (offer_accepted_certificate_info['certificate_start']):
                certification_info_obj.start_date = offer_accepted_certificate_info['certificate_start']
            if (offer_accepted_certificate_info['certificate_end']):
                certification_info_obj.end_date = offer_accepted_certificate_info['certificate_end']        
                 
        else:
            if (offer_accepted_certificate_info['certificate'] or offer_accepted_certificate_info['issued_by']):
                certification_info_obj = self.env['hr.experience.certification'].create({
                    'certifications' : offer_accepted_certificate_info['certificate'],
#                     'certificate_code' : offer_accepted_certificate_info['certificate_no'],
                    'issued_by' : offer_accepted_certificate_info['issued_by'],
                    'state_issued_id' : offer_accepted_certificate_info['state_issued_id'],
                    'start_date' : offer_accepted_certificate_info['certificate_start'] or False,
                    'end_date' : offer_accepted_certificate_info['certificate_end'] or False,
                    'employee_certification_id':form_id
                    })    
        certification_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        certification_info_obj.substate_id = 'medical'
        return certification_info_obj.substate_id
    
    def medicalinformation(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        if vals:
            medical_information_dict = {'vision': vals.vision or '',
                                        'chronic':vals.chronic or '',
                                        'undergone':vals.undergone or '',
                                        'cardiac':vals.cardiac or '',
                                        'frequent':vals.frequent or '',
                                        'others':vals.others or '',
                                       
                }
        return  medical_information_dict
    
    def insert_records_medical_info(self, form_id, medical_info):   
        medical_info_obj = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        if medical_info:
            medical_info_obj.chronic = medical_info['chronic'] 
            medical_info_obj.others = medical_info['other']
            medical_info_obj.vision = medical_info['vision']
            medical_info_obj.cardiac = medical_info['cardiac']
            medical_info_obj.frequent = medical_info['frequent']
            medical_info_obj.undergone = medical_info['undergone']
#             medical_info_obj.job_seniority_title = medical_info['seniority']
        medical_info_obj.substate_id = 'employement'
        
    def employementinfo(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
#         job_seniority = self.env['hr.job.seniority.title'].search([('id','in',vals.applied_job.job_template.job_seniority_id.ids)])
#         job_seniority_title_dict = {}
        seniority_id = self.env['hr.job.seniority.title'].sudo().search([])
        seniority = {}
        for lines in seniority_id:
            seniority.update({lines.id:lines.name})
#         for values in job_seniority:
#             job_seniority_title_dict.update({values.id:values.name})
#         con_type = self.env['hr.contract.type'].search([])
#         contract_types_dict={}
#         for lines in con_type:
#             contract_types_dict.update({lines.id:lines.name})
        employement_info_dict = {
                'contract_type' : vals.contract_type.id or '',
                'emp_start_date' : vals.emp_start_date or '',
#                 'benifits_seniority_date' : vals.benifits_seniority_date or '',
                'job_seniority_title' : vals.job_seniority_title.id or '',
                'seniority' : seniority,
#                 'contract_type_disp' : contract_types_dict,
            }
     
        return employement_info_dict
     
    def insert_records_employement_info(self, form_id, employement_info):
        employment_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if employement_info['job_seniority_title']:
            employment_info_obj.job_seniority_title = int(employement_info['seniority'])
        if employement_info['start_date']:
            employment_info_obj.emp_start_date = employement_info['start_date']
#         if employement_info['benefits_seniority_date']:
#             employment_info_obj.benifits_seniority_date = employement_info['benefits_seniority_date']
         
        employment_info_obj.substate_id = 'offer_summary'
 
#         if employment_info_obj.job_seniority_title and employment_info_obj.emp_start_date:
 
        return True    
    
    def offer_summary(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        emp_sts = self.env['hr.contract.type'].sudo().search([])
        emp_sts_dict = {}
        for lines in emp_sts:
            emp_sts_dict.update({lines.id:lines.name})

        state = self.env['res.country'].sudo().search([])
        state_dict = {}
        for lines in state:
            state_dict.update({lines.id:lines.name})

        exp_academic_list = []
        for line in vals.academic_experience_ids:
            exp_academic_list.append({
                'academic_tree_id' : line.id or '',
                'degree' : line.degree or '',
                'institute' : line.institute or '',
                'field_of_study' : line.field_of_study or '',
                'year_of_passing' : line.year_of_passing or '',
                'percentage' : line.percentage or '',
            })
            
        exp_professional_list = []
        for line in vals.professional_experience_ids:
            exp_professional_list.append({
                'professional_tree_id' : line.id or '',
                'position' : line.position or '',
                'organization' : line.organization or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        exp_certificate_list = []
        for line in vals.certification_ids:
            exp_certificate_list.append({
                'certification_tree_id' : line.id or '',
                'certifications' : line.certifications or '',
#                 'certificate_code' : line.certificate_code or '',
                'issued_by' : line.issued_by or '',
                'state_issued_id' : line.state_issued_id.name or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        offer_summary_dict = {
                'name' : vals.name or '',
                'mail' : vals.mail or '',
                'phone' : vals.phone or '',
                'responsible' : vals.responsible.name or '',
                'applied_job' : vals.applied_job.name or '',
                'company' : vals.company.name or '',
                'applicant_id' : vals.applicant_id,
                'emp_status': int(vals.emp_status.id) or '',
                'id_no' : vals.id_number or '',
                'passport_no' : vals.passport_number or '',
                'street' : vals.street or '',
                'street2' : vals.street2 or '',
                'city' : vals.city or '',
                'state' : vals.state.name or '',
                'country_id' : vals.country.name or '',
                'zip' : vals.zip or '',
                'gender' : vals.gender,
                'marital_status': vals.marital_status or '',
#                 'children' : vals.no_of_children or '',
                'dob' : vals.dob or '',
                'age' : vals.age or '',
                'emp_start_date' : vals.emp_start_date or '',
                'job_seniority_title' : vals.job_seniority_title.name or '',
#                 'benifits_seniority_date' : vals.benifits_seniority_date or '',
                'place_of_birth' : vals.place_of_birth or '',
                'nationality' : vals.nationality.name or '',
                'birth_country' : vals.birth_country.name or '',
                'scheduled_hours' : vals.scheduled_hours or '',
                'pay_rate' : vals.pay_rate or '',
                'emp_sts_disp' : emp_sts_dict,
                'exp_academic_list' : exp_academic_list or '',
                'exp_professional_list' : exp_professional_list or '',
                'exp_certificate_list' : exp_certificate_list or '',
                'state_dict' : state_dict or '',
#                 'emp_sts' : vals.emp_status.id,
                } 
        return offer_summary_dict
    
    def summary_state(self, form_id, summary_info):
        summary_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if (summary_info['summary_employment_status']):
            summary_obj.emp_status = int(summary_info['summary_employment_status'])
        if (summary_info['summary_scheduled_hours']):
            summary_obj.scheduled_hours = summary_info['summary_scheduled_hours'] or ''
        if (summary_info['summary_pay_rate']):
            summary_obj.pay_rate = summary_info['summary_pay_rate']
        
        if summary_obj.substate_id == 'offer_summary':
            summary_obj.substate_id = 'bgv'
            summary_obj.state_id = 'background'

    def bgv_info(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
                 
        bgv_list = []
        for line in vals.bgv_info_ids:
            bgv_list.append({
                'tree_id' : line.id or '',
                'name' : line.name or '',
                'mail' : line.email or '',
                'contact' : line.contact_no or '',
            })
        
        bgv_info_dict = {
                'bgv_list' : bgv_list or '',
            }
    
        return bgv_info_dict 

    def insert_records_bgv_info(self,form_id,bgv_info_vals):
        bgv_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if int(bgv_info_vals['form_bgv_tree_id'])>0:
            bgv_info_obj = self.env['background.verification'].search([('id' , '=' , bgv_info_vals['form_bgv_tree_id'])])
            if (bgv_info_vals['form_bgv_name']):
                bgv_info_obj.name = bgv_info_vals['form_bgv_name']
            if (bgv_info_vals['form_bgv_mail']):
                bgv_info_obj.email = bgv_info_vals['form_bgv_mail']
            if (bgv_info_vals['form_bgv_contact_no']):
                bgv_info_obj.contact_no = bgv_info_vals['form_bgv_contact_no']    
                 
        else:
            if (bgv_info_vals['form_bgv_name'] or bgv_info_vals['form_bgv_mail']):
                bgv_info_obj = self.env['background.verification'].create({
                    'name' : bgv_info_vals['form_bgv_name'],
                    'email' : bgv_info_vals['form_bgv_mail'],
                    'contact_no' : bgv_info_vals['form_bgv_contact_no'],
                    'bgv_info_id':form_id
                    })   

        bgv_obj.substate_id = 'background_check'
            
    def document_check(self, form_id):
        document_check_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])    
        if document_check_obj:
            document_check_dict = {'aadhar_card':document_check_obj.aadhar_card,
                                   'voter_id':document_check_obj.voter_id,
                                   'tenth_marksheet':document_check_obj.tenth_marksheet,
                                   'twelveth_marksheet':document_check_obj.twelveth_marksheet,
                                   'college_marksheet':document_check_obj.college_marksheet,
                                   'tc':document_check_obj.tc
                
                }   
            return document_check_dict 

    def insert_document_check(self, form_id, document_check_info):
        document_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if document_check_info['aadhar_card']:
            document_obj.aadhar_card = document_check_info['aadhar_card']
        if document_check_info['voter_id']:
            document_obj.voter_id = document_check_info['voter_id']    
        if document_check_info['tenth_marksheet']:
            document_obj.tenth_marksheet = document_check_info['tenth_marksheet']    
        if document_check_info['twelveth_marksheet']:
            document_obj.twelveth_marksheet = document_check_info['twelveth_marksheet']  
        if document_check_info['college_marksheet']:
            document_obj.college_marksheet = document_check_info['college_marksheet'] 
        if document_check_info['tc']:
            document_obj.tc = document_check_info['tc']
        document_obj.substate_id = 'summary_8'     
        
    def backgroundinfo(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        background_info_dict = {}
        if vals:
            background_info_dict = { 'tenure':vals.tenure or '',
                                    'cost_of_comapny':vals.cost_of_comapny or '',
                                    'reporting_manger_name':vals.reporting_manger_name or '',
                                    'reporting_manger_designation':vals.reporting_manger_designation or '',
                                    'reason_leaving':vals.reason_leaving or '',
                                    'attached_document':vals.attached_document or '',
                                    'feedback_on_account':vals.feedback_on_account or '',
                                    'source_of_verification':vals.source_of_verification or '',
                                    'exit_formalities':vals.exit_formalities or '',
                                    'designation':vals.designation or '',
                                    'employee_code':vals.employee_code or '',
                                    'reporting_manger_email_id':vals.reporting_manger_email_id or '',
                                    'reporting_manger_tele_no':vals.reporting_manger_tele_no or '',
                                    'eligibility_for_rehire':vals.eligibility_for_rehire or '',
                                    'referee_details':vals.referee_details or '',
                                    'date_and_time':vals.date_and_time or '',
                                    'notice_period':vals.notice_period or '',
                                    'any_other_commands':vals.any_other_commands or '',
                }
        return background_info_dict        
    
    def insert_records_backgroundinfo(self, form_id, background_check_info):
        background_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if background_check_info:
            background_obj.tenure = background_check_info['background_tenure']
            background_obj.cost_of_comapny = background_check_info['background_cost_of_comapny']
            background_obj.reporting_manger_name = background_check_info['background_reporting_manger_name']
            background_obj.reporting_manger_designation = background_check_info['background_reporting_manger_designation']
            background_obj.reason_leaving = background_check_info['background_reason_leaving']
            background_obj.attached_document = background_check_info['background_attached_document']
            background_obj.feedback_on_account = background_check_info['background_feedback_on_account']
            background_obj.source_of_verification = background_check_info['background_source_of_verification']
            background_obj.exit_formalities = background_check_info['background_exit_formalities']
            background_obj.designation = background_check_info['background_designation']
            background_obj.employee_code = background_check_info['background_employee_code']
            background_obj.reporting_manger_email_id = background_check_info['background_reporting_manger_email_id']
            background_obj.reporting_manger_tele_no = background_check_info['background_reporting_manger_tele_no']
            background_obj.eligibility_for_rehire = background_check_info['background_eligibility_for_rehire']
            background_obj.referee_details = background_check_info['background_referee_details']
            background_obj.date_and_time = background_check_info['background_date_and_time'] 
            background_obj.notice_period = background_check_info['background_notice_period']
            background_obj.any_other_commands = background_check_info['background_any_other_commands']
            background_obj.substate_id = 'document_check'
    
    def summarybackgroundinfo(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        summary_background_info_dict = {}
        if vals:
            summary_background_info_dict = { 'tenure':vals.tenure or ' ',
                                    'cost_of_comapny':vals.cost_of_comapny or '',
                                    'reporting_manger_name':vals.reporting_manger_name or '',
                                    'reporting_manger_designation':vals.reporting_manger_designation or '',
                                    'reason_leaving':vals.reason_leaving or '',
                                    'attached_document':vals.attached_document or '',
                                    'feedback_on_account':vals.feedback_on_account or '',
                                    'source_of_verification':vals.source_of_verification or '',
                                    'exit_formalities':vals.exit_formalities or '',
                                    'designation':vals.designation or '',
                                    'employee_code':vals.employee_code or '',
                                    'reporting_manger_email_id':vals.reporting_manger_email_id or '',
                                    'reporting_manger_tele_no':vals.reporting_manger_tele_no or '',
                                    'eligibility_for_rehire':vals.eligibility_for_rehire or '',
                                    'referee_details':vals.referee_details or '',
                                    'date_and_time':vals.date_and_time or '',
                                    'notice_period':vals.notice_period or '',
                                    'any_other_commands':vals.any_other_commands or '',
                                   'aadhar_card':vals.aadhar_card,
                                   'voter_id':vals.voter_id,
                                   'tenth_marksheet':vals.tenth_marksheet,
                                   'twelveth_marksheet':vals.twelveth_marksheet,
                                   'college_marksheet':vals.college_marksheet,
                                   'tc':vals.tc
                }
        return summary_background_info_dict
    
    def insert_record_summarybackgroundinfo(self, form_id):
        summary_background_obj = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        summary_background_obj.substate_id = 'app_summary'
        summary_background_obj.state_id = 'to_approve'
    
    def hire_summary(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        
        state = self.env['res.country'].sudo().search([])
        state_dict = {}
        for lines in state:
            state_dict.update({lines.id:lines.name})
            
        exp_academic_list = []
        for line in vals.academic_experience_ids:
            exp_academic_list.append({
                'academic_tree_id' : line.id or '',
                'degree' : line.degree or '',
                'institute' : line.institute or '',
                'field_of_study' : line.field_of_study or '',
                'year_of_passing' : line.year_of_passing or '',
                'percentage' : line.percentage or '',
            })
            
        exp_professional_list = []
        for line in vals.professional_experience_ids:
            exp_professional_list.append({
                 'professional_tree_id' : line.id or '',
                'position' : line.position or '',
                'organization' : line.organization or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
            
        exp_certificate_list = []
        for line in vals.certification_ids:
            exp_certificate_list.append({
                  'certification_tree_id' : line.id or '',
                'certifications' : line.certifications or '',
#                 'certificate_code' : line.certificate_code or '',
                'issued_by' : line.issued_by or '',
                'state_issued_id' : line.state_issued_id.name or '',
                'start_date' : line.start_date or '',
                'end_date' : line.end_date or '',
            })
        
        hire_summary_dict = {
                'name' : vals.name or '',
                'firstname' : vals.firstname or '',
                'lastname' : vals.lastname or '',
                'middlename' : vals.middlename or '',
                'mail' : vals.mail or '',
                'phone' : vals.phone or '',
                'responsible' : vals.responsible.name or '',
                'applied_job' : vals.applied_job.name or '',
                'company' : vals.company.name or '',
                'applicant_id' : vals.applicant_id,
                'emp_status': int(vals.emp_status.id) or '',
                'id_no' : vals.id_number or '',
                'passport_no' : vals.passport_number or '',
                'street' : vals.street or '',
                'street2' : vals.street2 or '',
                'city' : vals.city or '',
                'state' : vals.state.name or '',
                'country_id' : vals.country.name or '',
                'zip' : vals.zip or '',
                'gender' : vals.gender,
                'marital_status': vals.marital_status or '',
#                 'children' : vals.no_of_children or '',
                'dob' : vals.dob or '',
                'age' : vals.age or '',
                'emp_start_date' : vals.emp_start_date or '',
                'job_seniority_title' : vals.job_seniority_title.name or '',
#                 'benifits_seniority_date' : vals.benifits_seniority_date or '',
                'place_of_birth' : vals.place_of_birth or '',
                'nationality' : vals.nationality.name or '',
                'birth_country' : vals.birth_country.name or '',
                'scheduled_hours' : vals.scheduled_hours or '',
                'pay_rate' : vals.pay_rate or '',
                'exp_academic_list' : exp_academic_list or '',
                'exp_professional_list' : exp_professional_list or '',
                'exp_certificate_list' : exp_certificate_list or '',
                'state_dict' : state_dict or '',
                } 

        return hire_summary_dict
    
    def create_employee(self, form_id):

        create_employee_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if create_employee_obj.substate_id == 'app_summary':
            create_employee_obj.substate_id = 'ben_eligiblity'
        employee_id_exist = self.env['hr.employee'].search([('id', '=', create_employee_obj.employee_id.id)])
        if employee_id_exist:
            return employee_id_exist.id
        else:
            if not create_employee_obj.employee_id:
                employee = self.env['hr.employee'].create({
                    # 'name' : create_employee_obj.name or False,
                    'firstname' : create_employee_obj.firstname or False,
                    'middlename' : create_employee_obj.middlename or False,
                    'lastname' : create_employee_obj.lastname or False,
                    'address_id' : create_employee_obj.company.partner_id.id or False,
                    'work_phone' : create_employee_obj.phone or False,
                    'work_email' : create_employee_obj.mail or False,
                    'employment_status' : create_employee_obj.contract_type.id or False,
                    'country_id' : create_employee_obj.nationality.id or False,
                    'gender' : create_employee_obj.gender or False,
                    'birthday' : create_employee_obj.dob or False,
                    'company_id' : create_employee_obj.company.id or False,
                    'identification_id' : create_employee_obj.id_number or False,
                    'passport_id' : create_employee_obj.passport_number or False,
#                     'benefit_seniority_date' : create_employee_obj.benifits_seniority_date or False,
                    'start_date' : create_employee_obj.emp_start_date or False,
                    'job_id' : create_employee_obj.applied_job.id or False,
                    'job_seniority_title' : create_employee_obj.job_seniority_title.id or False,
                    'marital' : create_employee_obj.marital_status or False,
#                     'children' : create_employee_obj.no_of_children or False,
#                     'ethnic_id' : create_employee_obj.ethnic_id or False,
#                     'smoker' : create_employee_obj.smoker or False,
                    'place_of_birth' : create_employee_obj.place_of_birth or False,
                    'birth_country' : create_employee_obj.birth_country.id or False,
#                     'parent_id' :  manager_id.id or False,
                    'address_home_id' : create_employee_obj.partner_id.id or False,
                    'emergency_contact_name' : create_employee_obj.emergency_contact_name or False,
                    'emergency_contact_phone' : create_employee_obj.emergency_contact_phone or False,
                    'emergency_contact_relationship' : create_employee_obj.emergency_contact_relationship or False,
                    'notes' : create_employee_obj.notes or False,
                    'benefit_status' : 'not_eligible',
                    'overtime_pay' : 'non_exempt',
                    'aadhaar' : create_employee_obj.aadhaar or '',
#                     'pan' : create_employee_obj.pan or '',
#                     'pf' : create_employee_obj.pf or '',
#                     'esino' : create_employee_obj.esino or '',
                    'image' : create_employee_obj.image or '',

#                     'hire_date' : datetime.now().date(),
                    })
                create_employee_obj.employee_id = employee
                
                academics = self.env['hr.experience.academics'].search([('employee_academic_id', '=', create_employee_obj.id)])
                if academics:
                    for line in academics:
                        line.employee_exp_academic_id = create_employee_obj.employee_id.id
                professional = self.env['hr.experience.professional'].search([('employee_professional_id', '=', create_employee_obj.id)])
                if professional:
                    for line in professional:
                        line.employee_exp_professional_id = employee.id 
                certification = self.env['hr.experience.certification'].search([('employee_certification_id', '=', create_employee_obj.id)])        
                if certification:
                    for line in certification:
                        line.employee_exp_certification_id = employee.id           
                        
            return employee.id 
    
    def benefits_eligibility_info(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        ben_eligible_epf = ''
        ben_eligible_esi = ''
        ben_eligible_medical_policy = ''
        if(vals.benefits_epf):
            ben_eligible_epf = 'eligible'
        if(vals.benefits_esi):
            ben_eligible_esi = 'eligible'
        if(vals.benefits_medical_policy):
            ben_eligible_medical_policy = 'eligible'
        benefits_eligibility_dict = {
                'ben_eligible_epf' : ben_eligible_epf,
                'ben_eligible_esi' : ben_eligible_esi,
                'ben_eligible_medical_policy' : ben_eligible_medical_policy,
                'aadhaar' : vals.aadhaar or '',
                'pan' : vals.pan or '',
                'pf' : vals.pf or '',
                'esino' : vals.esino or '',
            }
        return benefits_eligibility_dict    

    def insert_vals_benefits_eligibility(self, form_id, benefits_epf, benefits_esi, benefits_medical_policy, benefits_eligibility_info):
        print(benefits_eligibility_info)
        ben_eligiblity_obj = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        if(benefits_epf == 'checked'):
            ben_eligiblity_obj.benefits_epf = True
        else:   
            ben_eligiblity_obj.benefits_epf = False 
        if(benefits_esi == 'checked'):
            ben_eligiblity_obj.benefits_esi = True
        else:
            ben_eligiblity_obj.benefits_esi = False    
        if(benefits_medical_policy == 'checked'):
            ben_eligiblity_obj.benefits_medical_policy = True
        else:
            ben_eligiblity_obj.benefits_medical_policy = False            
        if ben_eligiblity_obj.substate_id == 'ben_eligiblity':
            ben_eligiblity_obj.substate_id = 'welcome'    
        if benefits_eligibility_info['summary_aadhaar']:
            ben_eligiblity_obj.aadhaar = benefits_eligibility_info['summary_aadhaar']
            ben_eligiblity_obj.employee_id.aadhar_number =  benefits_eligibility_info['summary_aadhaar']
        if benefits_eligibility_info['summary_pan']:    
            ben_eligiblity_obj.pan = benefits_eligibility_info['summary_pan']
            ben_eligiblity_obj.employee_id.pan_number = benefits_eligibility_info['summary_pan']
        if benefits_eligibility_info['summary_pf']:    
            ben_eligiblity_obj.pf = benefits_eligibility_info['summary_pf']
            ben_eligiblity_obj.employee_id.epf_number = benefits_eligibility_info['summary_pf']
        if benefits_eligibility_info['summary_esino']:    
            ben_eligiblity_obj.esino = benefits_eligibility_info['summary_esino']
            ben_eligiblity_obj.employee_id.esino = benefits_eligibility_info['summary_esino']
    
# // checklist onboarding

    def onboadinginfo(self, form_id):
        print("eeeee")
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        board_nda = ''
        board_employeestatus = ''
        if(vals.on_nda):
            board_nda = 'eligible'
        if(vals.on_employeemanual):
            board_employeestatus = 'eligible'
        onboadinginfo_dict = {
                'board_nda' : board_nda,
                'board_employeestatus' : board_employeestatus,
            }
        
        print(onboadinginfo_dict)
        return onboadinginfo_dict    

    def insert_onboadinginfo(self, form_id, benefits_nda, benefits_employeemanual):
        onboarding_obj = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        if(benefits_nda == 'checked'):
            onboarding_obj.on_nda = True
        else:   
            onboarding_obj.on_nda = False 
        if(benefits_employeemanual == 'checked'):
            onboarding_obj.on_employeemanual = True
        else:
            onboarding_obj.on_employeemanual = False    

        onboarding_obj.substate_id = 'appraisal'
    
    def appraisal_info(self, form_id):
        vals = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        if vals.employee_id:
            appraisal_info_dict = {
                    'appraisal_by_manager' : vals.employee_id.appraisal_by_manager or '',
                    'appraisal_self' : vals.employee_id.appraisal_self or '',
                    'appraisal_by_tl' : vals.employee_id.appraisal_by_tl or '',
                    'appraisal_by_ro' : vals.employee_id.appraisals_by_ro or '',
                    'appraisal_by_hr' : vals.employee_id.appraisals_by_hr or '',
                    'periodic_appraisal' : vals.employee_id.periodic_appraisal or '',
                    'appraisal_frequency' : vals.employee_id.appraisal_frequency or '',
                    'appraisal_frequency_unit' : vals.employee_id.appraisal_frequency_unit or '',
                    'appraisal_date' : vals.employee_id.appraisal_date or '',
                    } 
            return appraisal_info_dict  
    
    def insert_records_appraisal_info(self, form_id, appraisal_plan_info):

        appraisal_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        emp_id = self.env['hr.employee'].search([('id' , '=' , appraisal_obj.employee_id.id)])
        if (appraisal_plan_info['apprasial_manager']):
            emp_id.appraisal_by_manager = appraisal_plan_info['apprasial_manager']  
#             appraisal_obj.appraisal_by_manager = appraisal_plan_info['manager']  
        if (appraisal_plan_info['employee']):
            emp_id.appraisal_self = appraisal_plan_info['employee']  
        if (appraisal_plan_info['tl']):
            emp_id.appraisal_by_tl = appraisal_plan_info['tl']  
        if (appraisal_plan_info['ro']):
            emp_id.appraisals_by_ro = appraisal_plan_info['ro']  
        if (appraisal_plan_info['hr']):
            emp_id.appraisals_by_hr = appraisal_plan_info['hr']  
        if (appraisal_plan_info['periodic_appraisal']):
            emp_id.periodic_appraisal = appraisal_plan_info['periodic_appraisal']  
        if (appraisal_plan_info['repeat_period']):
            emp_id.appraisal_frequency = appraisal_plan_info['repeat_period']  
            appraisal_obj.appraisal_frequency = appraisal_plan_info['repeat_period']  
        if (appraisal_plan_info['period']):
            emp_id.appraisal_frequency_unit = appraisal_plan_info['period']  
            appraisal_obj.appraisal_frequency_unit = appraisal_plan_info['period']  
        if (appraisal_plan_info['next_appraisal_date']):
            emp_id.appraisal_date = appraisal_plan_info['next_appraisal_date']  
            appraisal_obj.appraisal_date = appraisal_plan_info['next_appraisal_date']  

        if appraisal_obj.substate_id == 'welcome':
            appraisal_obj.substate_id = 'appraisal'
            appraisal_obj.state_id = 'contract'
            
    def employee_info(self, form_id):
        employee_summary_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        emp_id = self.env['hr.employee'].sudo().search([('id' , '=' , employee_summary_obj.employee_id.id)])
        
        employee_info_dict = {
                'name' : emp_id.name or '',
                'address_id' : emp_id.address_id.street or '',
                'street2' : emp_id.address_id.street2 or '',
                'city' : emp_id.address_id.city or '',
                'state' : emp_id.address_id.state_id.name or '',
                'country' : emp_id.address_id.country_id.name or '',
                'mobile_phone' : emp_id.mobile_phone or '',
                'work_email' : emp_id.work_email or '',
                'work_phone' : emp_id.work_phone or '',
                'job_id' : emp_id.job_id.name or '',
                'job_seniority_title' : emp_id.job_seniority_id.name or '',
                'department_id' : employee_summary_obj.applied_job.department_id.name or '',
                'resource_calendar_id' : emp_id.resource_calendar_id.name or '',
                'parent_id' : emp_id.parent_id.name or '',
                'coach_id' : emp_id.coach_id.name or '',
                'contract_type' : emp_id.contract_type.name or '',
                'manager_checkbox' : emp_id.manager or '',
                'country_id' : emp_id.country_id.name or '',
                'identification_id' : emp_id.identification_id or '',
                'passport_id' : emp_id.passport_id or '',
                'address_home_id' : emp_id.address_home_id.name or '',
                'gender' : emp_id.gender or '',
                'marital' : emp_id.marital or '',
                'children' : emp_id.children or '',
                'birthday' : emp_id.birthday or '',
                'place_of_birth' : emp_id.place_of_birth or '',
                'birth_country' : emp_id.birth_country.name or '',
                'age' : emp_id.age or '',
#                 'work_authorization' : emp_id.work_authorization or '',
#                 'document_no' : emp_id.document_no or '',
#                 'expiration_date' : emp_id.expiration_date or '',
#                 'document_A' : emp_id.document_A or '',
#                 'document_B' : emp_id.document_B or '',
#                 'document_C' : emp_id.document_C or '',
                'visa_no' : emp_id.visa_no or '',
                'permit_no' : emp_id.permit_no or '',
                'visa_expire' : emp_id.visa_expire or '',
#                 'timesheet_cost' : emp_id.timesheet_cost or '',
                'hire_date' : emp_id.hire_date or '',
                'user_id' : emp_id.user_id.name or '',
                'medic_exam' : emp_id.medic_exam or '',
                'vehicle' : emp_id.vehicle or '',
                'vehicle_distance' : emp_id.vehicle_distance or '',
                'remaining_leaves' : emp_id.remaining_leaves or '',
                'appraisal_self' : emp_id.appraisal_self or '',
                'appraisal_by_tl' : emp_id.appraisal_self or '',
                'appraisal_by_ro' : emp_id.appraisal_self or '',
                'appraisal_by_manager' : emp_id.appraisal_self or '',
                'appraisal_by_hr' : emp_id.appraisal_self or '',
                'periodic_appraisal' : emp_id.appraisal_self or '',
                'appraisal_date' : emp_id.appraisal_date or '',
                }
        
        if employee_summary_obj.substate_id == 'appraisal':
            employee_summary_obj.substate_id = 'employee_summary'
        return employee_info_dict
    
    def contract_info(self, form_id):
        form_info_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        contract_info_obj = self.env['hr.contract'].search([('id' , '=' , form_info_obj.new_contract_id.id)])
        if contract_info_obj:
            contract_info_dict = {
                'name' : contract_info_obj.name or '',
                'employee_id' : contract_info_obj.employee_id.name or '',
                'job_id' : contract_info_obj.job_id.name or '',
                'type_id' : contract_info_obj.type_id.name or '',
                'schedule_pay' : contract_info_obj.schedule_pay or '',
                'job_seniority_title' : contract_info_obj.job_seniority_id.name or '',
                'working_schedule' :  contract_info_obj.resource_calendar_id.name,
                'trial_date_start' : contract_info_obj.trial_date_start or '',
                'trial_date_end' : contract_info_obj.trial_date_end or '',
                'date_start' : contract_info_obj.date_start or '',
                'date_end' : contract_info_obj.date_end or '',
                'notes' : contract_info_obj.notes or '',
                'department_id' : contract_info_obj.department_id.name or '',
                'struct_id' : contract_info_obj.struct_id.name or '',
                'wage' : contract_info_obj.wage or '',
            }
            if form_info_obj.substate_id == 'create_contract':
                form_info_obj.substate_id = 'contract_summary'

            return contract_info_dict

        else:
            raise ValidationError(_('Please create contract by clicking "Click Here to Create Contract"'))
#         if form_info_obj.substate_id == 'create_contract':
#             form_info_obj.substate_id = 'contract_summary'
    
    def create_contract_via_link(self, form_id):
        create_contract_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
#         if create_contract_obj.substate_id=='contract':
#             create_contract_obj.substate_id = 'con_summary'
        contract_id_exist = self.env['hr.contract'].search([('employee_id', '=', create_contract_obj.employee_id.id)])
        if contract_id_exist:
            return contract_id_exist.id
        else:
            contract_id = self.env['hr.contract'].create({
                'employee_id' : create_contract_obj.employee_id.id,
                'name' : create_contract_obj.name,
                'job_seniority_id' : create_contract_obj.job_seniority_title.id,
                'type_id' : create_contract_obj.contract_type.id,
                'wage' : create_contract_obj.proposed_salary,
                'state' : 'open',
                'date_start' : create_contract_obj.employee_id.hire_date,
                'trial_date_start' : create_contract_obj.employee_id.hire_date,
                'job_id' : create_contract_obj.employee_id.job_id.id,
                'department_id' : create_contract_obj.employee_id.department_id.id,
                'benefits_epf':create_contract_obj.benefits_epf,
                'benefits_esi':create_contract_obj.benefits_esi,
                'benefits_medical_policy':create_contract_obj.benefits_medical_policy,
                'department_id':create_contract_obj.applied_job.department_id.id,
                })
            create_contract_obj.new_contract_id = contract_id.id
#         if create_contract_obj.substate_id == 'contract_summary':
#             create_contract_obj.substate_id = 'create_contract'    
        return contract_id.id    
    
    @api.multi
    def send_launch_pack(self, form_id, check_id, get_started):
        send_obj = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
        req_id = 0
        if send_obj.substate_id == 'started':
            if check_id == 'launch':
                self.insert_records_get_started(form_id, get_started, from_pid=1)
            if form_id:
                employee_obj = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
                if employee_obj.mail:
                    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", employee_obj.mail) != None:
#                         personal_doc_obj = self.env['employee.settings'].search([('emp_contract_type' , 'in' , [employee_obj.contract_type.id])], limit=1)
                        get_temp_id = self.get_values()
                        template_ids = []
                        template_id = self.env['signature.request.template'].search([('id', '=', get_temp_id['pi_document_id'])])
                       
                        if template_id:
                            req_id = ''
                            reference = template_id.attachment_id.name
                            request_item = self.env["signature.item"].search([('template_id', '=', template_id.id)])
                            
                            roles = []
                            for req_item in request_item:
                                if req_item.responsible_id.id not in roles:
                                    roles.append(req_item.responsible_id.id)
                            template_ids.append((template_id.id, reference))
#                             applicant_obj = self.env['hr.applicant'].search([('id' , '=' , employee_obj.applicant_id)])
                            partner = self.env['res.partner'].search([('applicant_id', '=', int(employee_obj.applicant_id))])
                            if partner:
                                if template_ids:
                                    signers = []
                                    signer = {}
                                    for role in roles:
                                        signer = {
                                        'partner_id' : partner.id,
                                        'role': role
                                        }
                                        signers.append(signer)
                                    req_id = self.env["signature.request"].with_context({'template_id': template_ids, 'reference': template_ids, 'status':'launch'}).initialize_new(template_ids[0][0], signers, followers=[], reference=reference, subject="", message="", send=True)
                                    employee_obj.pid_document_id = req_id['id']
                                
#                             else:
#                                 pay_term = self.env['account.payment.term'].search([('name', '=', 'Immediate Payment')]).id
#                                 pay_mode = self.env['account.payment.mode'].search([('name', '=', 'Manual Payment')]).id
#                                 rel_user = self.env['res.partner'].create({
#                                     'firstname' : employee_obj.first_name or False,
#                                     'middlename' : employee_obj.middle_name or False,
#                                     'lastname' : employee_obj.last_name or False,
#                                     'email' : employee_obj.mail or False,
#                                     'company_id' : employee_obj.company.id or False,
#                                     'property_supplier_payment_term_id' : pay_term or False,
#                                     'supplier_payment_mode_id' : pay_mode or False,
#                                     'state_id' : employee_obj.state.id or False,
#                                     'city' : employee_obj.city or False,
#                                     'street' : employee_obj.street or False,
#                                     'street2' : employee_obj.street2 or False,
#                                     'country_id' : employee_obj.country.id or False,
#                                     'zip' : employee_obj.zip or False,
#                                     })
#                                 applicant_obj.partner_id = rel_user
#                                 employee_obj.partner_id = rel_user
#                                 if template_ids:
#                                     signers = []
#                                     signer = {}
#                                     for role in roles:
#                                         signer={
#                                         'partner_id' : rel_user.id,
#                                         'role': role
#                                         }
#                                         signers.append(signer)
# 
#                                     req_id = self.env["signature.request"].with_context({'template_ids': template_ids, 'reference': template_ids,'status':'launch'}).initialize_new(template_ids[0][0], signers, followers=[], reference=reference, subject="", message="", send=True)
#                                     employee_obj.pid_document_id = req_id['id']

                        else:
                            raise ValidationError("Please select Personal Information document in configurations")
                    else:
                        raise ValidationError("Please enter a valid email or check the spaces before and after the email id")
            return req_id

        else:
            return req_id
    
    def contract(self, form_id):
        contract_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if contract_obj.substate_id == 'employee_summary':
            contract_obj.substate_id = 'create_contract' 
        return    
        
    def smart_buttons(self, form_id):
        button_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        smart_button_dict = {
            'applicant_id' : button_obj.applicant_id,
        }

        return smart_button_dict
                
    @api.model
    def get_values(self):
        res = {}
        res.update(welcome_template_id=self.env['ir.config_parameter'].sudo().get_param('ppts_onboarding.welcome_template_id'),
                   pi_document_id=self.env['ir.config_parameter'].sudo().get_param('ppts_onboarding.pi_document_id')
                  )
        
        return res
      
    def welcome_mail(self, form_id):
        get_mail_id = self.get_values()
        
        if get_mail_id:
            welcome_mail_id = self.env['mail.template'].search([('id', '=', get_mail_id['welcome_template_id'])])
        return welcome_mail_id.name
    
    def send_welcome_email(self, form_id):
        get_mail_id = self.get_values()
        if get_mail_id:
            welcome_mail_id = self.env['mail.template'].search([('id', '=', get_mail_id['welcome_template_id'])])
            current_id = self.env['hr.employee.onboarding'].search([('id', '=', form_id)])
            print(welcome_mail_id, current_id)
            welcome_mail_id.sudo().send_mail(current_id.id, force_send=True)
            current_id.substate_id = 'on_boardingchecklist'
        return True
    
    def complete(self, form_id):
        complete_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])
        if complete_obj.substate_id == 'contract_summary':
            complete_obj.substate_id = 'completed'
            complete_obj.state_id = 'complete'  
        return True      
    
#     def document(self,form_id):
#         document_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)])  
#         if document_obj:
#             document = {}      
    
    def get_sub_state_id(self, form_id):
        if form_id != 'GetStarted0':
            complete_state_obj = self.env['hr.employee.onboarding'].search([('id' , '=' , form_id)]) 
            sub_state = [('started', 'GetStarted0'),
                         ('personal', 'PersonalInformation1'),
                         ('experience', 'ExperienceandCertifications2'),
                         ('medical', 'MedicalInformation3'),
                         ('employement', 'EmployementInformation4'),
                         ('offer_summary', 'Summary5'),
                         ('bgv','BackgroundVerification6'),
                         ('background_check', 'BackgroundCheck7'),
                         ('document_check', 'DocumentCheck8'),
                         ('summary_8', 'Summary9'),
                         ('app_summary', 'ApplicantSummary/Hire10'),
                         ('ben_eligiblity', 'BenefitsEligibility11'),
                         ('welcome', 'WelcomeEmail12'),
                         ('on_boardingchecklist', 'OnboardingChecklist13'),
                         ('appraisal', 'AppraisalPlan14'),
                         ('employee_summary', 'EmployeeSummary15'),
                         ('create_contract', 'CreateContract16'),
                         ('contract_summary', 'ContractSummary17'),
                         ('completed', 'Complete18')]   
            return [item[1] for item in sub_state if item[0] == complete_state_obj.substate_id][0]


    @api.multi
    def send_bgv_survey(self,form_id,tree_id,doc_id):
        if form_id:
            onboarding_obj = self.env['hr.employee.onboarding'].search([('id','=',form_id)])
            if int(tree_id) == 0:
                # onboarding_obj.insert_records_bgv_info(form_id,doc_id)
                if (doc_id['form_bgv_name'] or doc_id['form_bgv_mail']):
                    bgv_obj = self.env['background.verification'].create({
                        'name' : doc_id['form_bgv_name'],
                        'email' : doc_id['form_bgv_mail'],
                        'contact_no' : doc_id['form_bgv_contact_no'],
                        'bgv_info_id':form_id
                        })
            else:
                bgv_obj = self.env['background.verification'].search([('id','=',tree_id)])
                if (doc_id['form_bgv_name']):
                    bgv_obj.name = doc_id['form_bgv_name']
                if (doc_id['form_bgv_mail']):
                    bgv_obj.email = doc_id['form_bgv_mail']
                if (doc_id['form_bgv_contact_no']):
                    bgv_obj.contact_no = doc_id['form_bgv_contact_no'] 

            get_temp_id = self.env['onboarding.config.settings'].get_values()

            survey_obj = self.env['survey.survey'].search([('id','=', get_temp_id['bgv_survey_id'])])

            survey_link = []
            survey_list = []
            bgv_survey_info= ''

            token = uuid.uuid4().__str__()

            print(onboarding_obj.partner_id)

            survey_id_obj = self.env['survey.user_input'].create({
                'survey_id': survey_obj.id,
                'date_create': fields.Datetime.now(),
                'type': 'link',
                'state': 'new',
                'token': token,
                'partner_id': onboarding_obj.partner_id.id,
                'email': bgv_obj.email,
                'onboarding_id' : form_id})
            survey_list.append(survey_id_obj.id)

            if survey_id_obj:
                bgv_obj.survey_id = survey_id_obj.id

            self.env.cr.execute("select survey_id,token from survey_user_input where onboarding_id="+form_id)
            results = self.env.cr.dictfetchall()

            final_result = self.env['survey.user_input'].sudo().search([('onboarding_id' , '=' , int(form_id))],limit=1)

            print (final_result)

            for record in final_result:
                survey = self.env['survey.survey'].search([('id' , '=' , record.survey_id.id)])
                base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
                public_url = urljoin(base_url, "survey/start/%s" % (slug(survey)))
                bgv_survey_info = public_url+"/"+record.token
                survey_link.append(bgv_survey_info)
                print(survey_link)

            template_id = self.env.ref('ppts_onboarding.email_template_bgv_survey').id
            mail_template = self.env['mail.template'].browse(template_id)

            attachment_list = []

            for attchment in bgv_obj.attachment_ids:
                attachment_list.append(attchment.id)

            print(bgv_obj.attachment_ids.ids,'attachment_list',attachment_list)

            if mail_template:
                mail_template.attachment_ids.unlink()
                mail_template.attachment_ids = attachment_list
                mail_template.with_context(survey_link=survey_link).send_mail(bgv_obj.id, force_send=True)

            onboarding_obj.benefits_states = 'progress'
        
    
class AcademicExperiences(models.Model):
    _inherit = "hr.experience.academics"
    
    employee_academic_id = fields.Many2one('hr.employee.onboarding', string="Academic")

    
class ProfessionalExperiences(models.Model):
    _inherit = "hr.experience.professional"
    
    employee_professional_id = fields.Many2one('hr.employee.onboarding', string="Professional")

    
class CertificationDetail(models.Model):
    _inherit = "hr.experience.certification"
    
    employee_certification_id = fields.Many2one('hr.employee.onboarding', string="Certification")

class BackgroundVerificationInfo(models.Model):
    _name = "background.verification"
    
    name = fields.Char("Name")
    email = fields.Char("Email")
    contact_no = fields.Char("Contact No")
    survey_id = fields.Many2one('survey.user_input',string='BGV Survey')
    # documents = fields.Binary('Documents')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'message_attachment_rel',
        'message_id', 'attachment_id',
        string='Documents')
    bgv_info_id = fields.Many2one('hr.employee.onboarding', string="BGV Info Ref")

    
class SignatureRequestItem(models.Model):
    _inherit = "signature.request.item"
    
    @api.multi
    def send_signature_accesses(self, subject=None, message=None):
        base_context = self.env.context
        if self.env.context.get('status') == 'launch':
            template_id = self.env.ref('ppts_onboarding.onboarding_launch_pack').id
      
        mail_template = self.env['mail.template'].browse(template_id)

        email_from_usr = self[0].create_uid.partner_id.name
        email_from_mail = self[0].create_uid.partner_id.email
        email_from = "%(email_from_usr)s <%(email_from_mail)s>" % {'email_from_usr': email_from_usr, 'email_from_mail': email_from_mail}
        link_list = []

        if self.env.context.get('status') == 'launch':
            for signer in self:
                if not signer.partner_id:
                    continue
                template = mail_template.sudo().with_context(base_context,
                    partner_name=signer.partner_id.name,
                    lang=signer.partner_id.lang,
                    template_type="request",
                    email_from_usr=email_from_usr,
                    email_from_mail=email_from_mail,
                    email_from=email_from,
                    email_to=signer.partner_id.email,
                    link="sign/document/%(request_id)s/%(access_token)s" % {'request_id': signer.signature_request_id.id, 'access_token': signer.access_token},
                    subject=subject or ("Signature request - " + signer.signature_request_id.reference),
                    msgbody=(message or "").replace("\n", "<br/>")
                )
                template.send_mail(signer.signature_request_id.id, force_send=True)

        else:
            for signer in self:
                if not signer.partner_id:
                    continue
                template = mail_template.sudo().with_context(base_context,
                    lang=signer.partner_id.lang,
                    template_type="request",
                    email_from_usr=email_from_usr,
                    email_from_mail=email_from_mail,
                    email_from=email_from,
                    email_to=signer.partner_id.email,
                    link="sign/document/%(request_id)s/%(access_token)s" % {'request_id': signer.signature_request_id.id, 'access_token': signer.access_token},
                    subject=subject or ("Signature request - " + signer.signature_request_id.reference),
                    msgbody=(message or "").replace("\n", "<br/>")
                )
                template.send_mail(signer.signature_request_id.id, force_send=True)
              
