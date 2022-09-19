from odoo import fields, models, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Employee(models.Model):
    _inherit = "hr.employee"
    
    def overall_tenure(self):
        employee_id = self.env['hr.employee'].search([])
        for rec in employee_id:
            if rec.doj:
                fmt = '%Y-%m-%d'
                doj = datetime.strptime(rec.doj, fmt)
                date_now = datetime.now()
                rdelta = relativedelta(date_now, doj)
                months_tol = (rdelta.years * 12) + rdelta.months
                rec.date_diff = months_tol
    
    def experience_tenure(self):
        employee_id = self.env['hr.employee'].search([])
        for rec in employee_id:
            for row in rec.employee_professional_experience_ids:
                if row.start_date and row.end_date:
                    fmt = '%Y-%m-%d'
                    start_date = datetime.strptime(row.start_date, fmt)
                    end_date = datetime.strptime(row.end_date, fmt)
                    rdelta = relativedelta(end_date, start_date)
                    months_tol = (rdelta.years * 12) + rdelta.months
                    row.tenure = months_tol
                
    age = fields.Integer("Age", track_visibility='onchange')
    birth_country = fields.Many2one('res.country', string="Birth Country")
    job_seniority_id = fields.Many2one('hr.job.seniority.title', string="Job seniority title")
    contract_type = fields.Many2one('hr.contract.type', string="Contract Type")
    hire_date = fields.Date(string="Hire Date", default=datetime.today())
    demographic = fields.Boolean("Demographic", help='Sends mail about this employee to the concerned person if this checbox is not checked.')
    
    client_code = fields.Char("Client code", track_visibility='onchange')
    present_team = fields.Char("Present Team", track_visibility='onchange')
    present_salary = fields.Float("Present Salary", track_visibility='onchange')
    
    native = fields.Char("Native", track_visibility='onchange')
    date_of_marriage = fields.Date(string="Date of Marriage", track_visibility='onchange')
    religion = fields.Char("Religion", track_visibility='onchange')
    caste = fields.Char("Caste", track_visibility='onchange')
    community = fields.Char("Community", track_visibility='onchange')
    mother_tounge = fields.Char("Mother Tounge", track_visibility='onchange')    
    blood_group_id = fields.Many2one('blood.group.master',string='Blood Group', track_visibility='onchange')
    blood_group = fields.Char("Blood Group", track_visibility='onchange')
    identification_mark = fields.Text("Identification Mark", track_visibility='onchange')
    
    pass_do_issue = fields.Date("DO Issue", track_visibility='onchange')
    pass_do_expiry = fields.Date("DO Expiry", track_visibility='onchange')
    pass_place_issue = fields.Char("Place of Issue", track_visibility='onchange')
    abroad_trip = fields.Char("Abroad trip if any", track_visibility='onchange')
    
    dl_no = fields.Char("Driving Licence No", track_visibility='onchange')
    dl_do_issue = fields.Date("DO Issue", track_visibility='onchange')
    dl_do_expiry = fields.Date("DO Expiry", track_visibility='onchange')
    dl_place_issue = fields.Char("Place of Issue", track_visibility='onchange')
    athorised_drive = fields.Char("Class of vehicles athorised to drive", track_visibility='onchange')
    
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    residence_year = fields.Char("Total year of residence")
    landline_no = fields.Char("Landline Number")
    
    present_address = fields.Boolean("Is this Present Address")
    street_1 = fields.Char()
    street2_1 = fields.Char()
    zip_1 = fields.Char(change_default=True)
    city_1 = fields.Char()
    state1_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', domain="[('country_id', '=?', country_id)]")
    country1_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    residence_year_1 = fields.Char()
    landline_no_1 = fields.Char()
    email = fields.Char()
    
    accomodation_ids = fields.One2many('accomodation.details','employee_id', string='Accomodation Details')
    guardian_ids = fields.One2many('guardian.details','employee_id', string='Guardian Details')
    family_ids = fields.One2many('family.details','employee_id', string='Family Details')
    
    hobbies = fields.Char("Hobbies")
    talents = fields.Char("Talents")
    lang_known_ids = fields.One2many('language.known','employee_id', string='Languages Known')
    
    doj = fields.Date("Date of Join", track_visibility='onchange')
    do_confirm = fields.Date("Date of Confirmation", track_visibility='onchange')
    probation_period = fields.Date("Probation Period", track_visibility='onchange')
    stamping = fields.Char("Stamping/Checking Autority") 
    date_diff = fields.Char('Overall Tenure (Months)', readonly=True, default='0')
    
    designation_ids = fields.One2many('designation.held','employee_id', string='Designations Held')
    salary_ids = fields.One2many('salary.details','employee_id', string='Salary Details')
    original_certificate_ids = fields.One2many('original.certificate','employee_id', string='Original Certificates')
    other_certificate_ids = fields.One2many('other.certificate','employee_id', string='Other Certificates')
    reference_ids = fields.One2many('reference.details','employee_id', string='Details of Reference')

    medical_1 = fields.Char("Vision") 
    medical_2 = fields.Char("Cardiac") 
    medical_3 = fields.Char("Chronic Illness(Long term illness like wheezing,asthma,diabetics,allergies,etc.")
    medical_4 = fields.Char("Frequent headache,migrane,backpain,etc.") 
    medical_5 = fields.Char("Undergone any surgery in the past or met with an accident") 
    medical_6 = fields.Char("Any other in specific")
    
    hr_notes = fields.Text("HR Notes")
    training = fields.Text("Traning")
    
    resignation_ids = fields.One2many('resignation.details','employee_id', string='Resignation Details')
    
    @api.onchange('birthday')
    def onchange_age(self):
        today = datetime.now().date()
        bday = datetime.strptime(self.birthday, '%Y-%m-%d').date()
        self.age = today.year - bday.year

    def date_recipt_update(self):
        employee_obj = self.env['hr.employee'].search([])

        for rec in employee_obj:
            for val in rec.original_certificate_ids:
                if rec.doj:
                    val.date_receipt = rec.doj

    def partner_name_update(self):
        partner_obj = self.env['res.partner'].search([])
        for partner in partner_obj:
            if partner.email:
                applicant_obj = self.env['hr.applicant'].search([('email_from', '=' , partner.email)])
                if applicant_obj:
                    partner.partner_name = str(applicant_obj.partner_name or '') + ' ' + str(applicant_obj.middlename or '') + ' ' + str(applicant_obj.lastname or '')
                    partner.employee = True
                    partner.customer = False
                    partner.billing = False

# // Cron to fill the assigned and eligible employees
    @api.model
    def mail_to_hr(self):
        employees_ids = self.env['hr.employee'].search([('demographic', '=', False)])
        print('----',employees_ids,'----')
        template_id = self.env.ref('ppts_employee_additional_fields.hr_employees_email')        
        emp_list = []
        for value in employees_ids:
            
            qualification = self.env['hr.experience.academics'].search([('employee', '=', value.id)], limit=1)
            previous_company = self.env['hr.experience.professional'].search([('employee', '=', value.id)], limit=1)
            source_exp = self.env['hr.applicant'].search([('email_from', '=', value.work_email)])
            
            emp_details = {}
            emp_details['name'] = value.name
            emp_details['image'] = value.image_medium
            emp_details['birthday'] = str(value.age) + '&' + str(value.birthday)
            emp_details['department'] = value.department_id.name
            emp_details['designation'] = value.job_id.name
            emp_details['date_of_joining'] = value.date_of_joining
            emp_details['address'] = str(value.address_home_id.street) + ',' + str(value.address_home_id.street2) + ',' + str(value.address_home_id.city) + ',' + str(value.address_home_id.state_id.name) + ',' + str(value.address_home_id.country_id.name) + ',' + str(value.address_home_id.zip) 
            emp_details['qualification'] = str(qualification.degree) + '&' + str(qualification.institute)
            emp_details['previous_company'] = previous_company.organization
            emp_details['source'] = source_exp.source_id.name
            emp_details['experience'] = source_exp.exp_in_month
            
            emp_list.append(emp_details)

            value.demographic = True

        if template_id:
            template_id.with_context({'emp_list': emp_list, }).send_mail(self.id, force_send=True)

class DesignationHeld(models.Model):
    _name = 'designation.held'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    designation = fields.Char("Designation", required=True)
    wef = fields.Date("W.E.F", required=True)
    
class SalaryDetails(models.Model):
    _name = 'salary.details'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    amount = fields.Float("Amount", required=True)
    wef = fields.Date("W.E.F", required=True)
    
class AccomodationDetails(models.Model):
    _name = 'accomodation.details'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    present_accom_address = fields.Char("Present Accomodation Address", required=True)
    room_mates = fields.Char("Room Mates Details")
    contact_no = fields.Char("Contact Number")
    
class GuardianDetails(models.Model):
    _name = 'guardian.details'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    guardian_name = fields.Char("Guardian Name", required=True)
    relationship = fields.Char("Relationships")
    emergency_address = fields.Text("Address")
    contact_no = fields.Char("Contact Number")
    
class FamilyDetails(models.Model):
    _name = 'family.details'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    relationship = fields.Char("Relationships")
    name = fields.Char("Name", required=True)
    age = fields.Integer("Age")
    qualification = fields.Char("Qualification")
    occupation = fields.Char("Occupation")
    income = fields.Char("Annual Income")
    contact = fields.Char("Contact")
    
class LanguageKnown(models.Model):
    _name = 'language.known'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    # name = fields.Char("Language", required=True)
    language_id = fields.Many2one('language.master',string="Language")
    is_read = fields.Boolean("Read")
    is_write = fields.Boolean("Write")
    is_speak = fields.Boolean("Speak")

class LanguageMaster(models.Model):
    _name = 'language.master'

    name = fields.Char('Language Name')
    
class OriginalCertificate(models.Model):
    _name = 'original.certificate'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    certificate = fields.Char("Certificate", required=True)
    reg_no = fields.Char("Certificate/Reg.no")
    date_receipt = fields.Date("Date of Receipt")
    
class OtherCertificate(models.Model):
    _name = 'other.certificate'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    certificate = fields.Char("Academic Certificate", required=True)
    blood_group = fields.Char("Blood Group Proof")
    medical_certificate = fields.Char("Medical Fitness Certificate")
    address_proof = fields.Char("Address Proof")
    id_proof = fields.Char("Id Proof")
    other_certificate = fields.Char("Other Certificates")

class BloodGroupMaster(models.Model):
    _name = 'blood.group.master'

    name = fields.Char('Blood Group Name')
    
class ReferenceDetails(models.Model):
    _name = 'reference.details'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    ref_done_by = fields.Char("Reference Check done by", required=True)
    ref_name = fields.Char("Name of the referer")
    relationship = fields.Char("Relationships")
    contact = fields.Char("Contact Details")
    ref_date = fields.Date("Date of reference")
    ref_comment = fields.Text("Reference Comments")
    
class ResignationDetails(models.Model):
    _name = 'resignation.details'
    
    employee_id = fields.Many2one('hr.employee',string="Employee")
    do_resignation = fields.Date("DO Resignation Notice", required=True)
    last_day = fields.Date("Last Working Day")
    do_releiving = fields.Date("DO Releiving/Termination")
    certificate_issue = fields.Date("Certificates issued on")
    reason = fields.Text("Reason")
    exit_interview = fields.Date("Exit interview")
    comments = fields.Text("Comments")
    
    
    