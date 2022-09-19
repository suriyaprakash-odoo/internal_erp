# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools.safe_eval import safe_eval
import pytz, datetime
from datetime import datetime, date, timedelta
from werkzeug import urls
from odoo.tools.mail import reference_re
from werkzeug.urls import url_join
experience_year = []
for year in range(0, 11):
    experience_year.append((str(year), str(year)))
DOCUMENTS = [
    {'doc_name':"Organization Name",'count':0},
    {'doc_name':"Work Location",'count':0},
    {'doc_name':"Date of Joining",'count':0},
    {'doc_name':"Date of Leaving",'count':0},
     {'doc_name':"Tenure",'count':0},
      {'doc_name':"Designation Held",'count':0},
       {'doc_name':"Total Salary per month",'count':0},
        {'doc_name':"Reasons for change",'count':0},
    ]    
class RecruitmentStage(models.Model):
    _inherit = "hr.recruitment.stage"
    
    stage_code = fields.Char(string='Stage Code')
    survey_id = fields.Many2one("survey.survey",string="Survey")

class JobSeniorityTitle(models.Model):  
    _name = "hr.job.seniority.title"
    name = fields.Char(string="Display Title")
    sequence = fields.Integer(string="Sequence")
    
    
    _sql_constraints = [
        ('sequence_uniq', 'unique (sequence)','Sequence Number must be unique')]
   
    
    @api.model
    def create(self, vals):
        if vals['sequence']<1:
            raise UserError('Sequence Number must be greater than 0')
        line = super(JobSeniorityTitle, self).create(vals)
        return line

    @api.multi
    def write(self, vals):
        if vals.get('sequence'):
            sequence = vals.get('sequence')
        else:
            sequence = self.sequence
        for employee in self.env['hr.employee'].search([('job_seniority_id','=',self.id)]):
            employee.sequence = sequence
        
        return super(JobSeniorityTitle, self).write(vals)


# class Job(models.Model):

#     _inherit = 'hr.job'


#     @api.multi
#     def website_publish_button(self):
#         # self.ensure_one()
#         # if self.env.user.has_group('website.group_website_publisher') and self.website_url != '#':
#         #     return self.open_website_url()
#         return self.write({'website_published': True})

#     @api.multi
#     def set_open(self):
#         self.write({'website_published': False})
#         return super(Job, self).set_open()
    

class JobTemplate(models.Model):
    _name = "hr.job.template"
    
    
    name = fields.Char("Name",required=True)   
    active_state = fields.Boolean("Active",default=True)
    job_description = fields.Text("Job Description")
    department_id = fields.Many2one("hr.department",string="Department")
    introduction = fields.Text("Introduction")
    application_survey_id = fields.Many2one("survey.survey",string="Applicant Survey")
    interviewer_survey_id = fields.Many2one("survey.survey",string="Interviewer Survey")
    email_template_id = fields.Many2one("mail.template",string="Offer Email Template")
    job_seniority_id = fields.Many2many("hr.job.seniority.title",string="Job seniority title",required=True)
    sign_document_id = fields.Many2one("signature.request.template",string="CIF Document")

class Survey(models.Model):
    """ Settings for a multi-page/multi-question survey.
        Each survey can have one or more attached pages, and each page can display
        one or more questions.
    """

    _inherit = 'survey.survey'

    applicant_id = fields.Many2one('hr.applicant',string="Applicant")


class Applicant(models.Model):
    _inherit = "hr.applicant"
    
    p_country = fields.Many2one('res.country',string="Country")
    l1_round = fields.Boolean(string='L1',readonly=True)
    l2_round = fields.Boolean(string='L2',readonly=True)
    manager = fields.Boolean(string='Manager',readonly=True)
    stage_check = fields.Char(related='stage_id.name',string='Stage Check',readonly=True)
    sex_type = fields.Selection([('male','Male'),('female','Female')],string = 'Sex')
    gender_type = fields.Selection([('male', 'Male'), ('female', 'Female')])
    negotiate = fields.Selection([('yes', 'Yes'), ('no', 'No')],string = 'Negotiable')
    shift_time = fields.Selection([('yes', 'Yes'), ('no', 'No')],string = 'Will you be willing to work in shifts')
    selected_days = fields.Char(string='If selected, when can you join (in days)?')
    applicant_applied = fields.Char(string='Position applied for')
    date_birth = fields.Date('Date of Birth') 
    age = fields.Integer('Age')
    age_year = fields.Char("Years")
    so_channel = fields.Char(string='Sourcing Channel')
    salary_expextation = fields.Char(string='Salary expected per month')
    name_so = fields.Char(string='Name of the Source')
    present_state = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    present_check = fields.Boolean(string='Is Present Address',default=False)
    present_address = fields.Text(string='Present Address')
    present_applicant_street = fields.Char()
    city = fields.Char(string='City')
    pin = fields.Char(string='Pincode')
    tel_no = fields.Char(string='Tel No(Off)')
    resi = fields.Char(string='(Resi)')
    mobile = fields.Char(string='Mobile')
    e_mail = fields.Char(string='E-mail')
    present_country = fields.Many2one('res.country',string="Country")
    permanent_state = fields.Many2one("res.country.state", string='State', ondelete='restrict')
    permanent_address = fields.Char(string='Permanent Address')
    applicant_street = fields.Char()
    p_city = fields.Char(string='City')
    p_pin = fields.Char(string='Pincode')
    p_tel_no = fields.Char(string='Tel No(Off)')
    p_resi = fields.Char(string='(Resi)')
    p_mobile = fields.Char(string='Mobile')
    p_e_mail = fields.Char(string='E-mail')
    family_history = fields.Char(string='Family History')
    reference_details = fields.Char(string='References: (Please give details of 2 persons of your current organization[HR,TL,Managers]. Relations and friends cannot be referred) ')
    status_type = fields.Selection([('single', 'Single'), ('married', 'Married'),('widower', 'Widower'),('divorced', 'Divorced')],string='Marital status')
    applicant_lang_ids = fields.One2many("applicant.lang.item", "app_lang_id", string="Language Known ")
    applicant_detail_ids = fields.One2many("applicant.details.item","applicant_detail_id", string="Family History ")
    applicant_reference_ids = fields.One2many("applicant.reference.details","applicant_reference_id", string="Reference History ")
    applicant_work_ids = fields.One2many("applicant.work.details","applicant_work_id", string="Work History ",default=DOCUMENTS)

    stage_change_flag = fields.Selection([('new','New'),
                                          ('scheduled','Scheduled'),
                                          ('offer','Offer'),
                                          ('tech','Technical Discussion'),
                                          ('man','Manager Discussion'),
                                          ('final','Final Discussion')],'Stage Flag', compute = '_stage_change_flag')

    new_stage_feebdack = fields.Text(string='Feedback - New Applicant',track_visibility='onchange')
    technical_stage_feebdack = fields.Text(string='Feedback - Technical Round',track_visibility='onchange')
    manager_stage_feebdack = fields.Text(string='Feedback - Manager Round',track_visibility='onchange')
    final_stage_feebdack = fields.Text(string='Feedback - Final Discussion',track_visibility='onchange')

    hr_discussion_survey = fields.Many2one('survey.survey',string = 'Scheduled Survey')
    tech_discussion_survey = fields.Many2one('survey.survey',string = 'Technical Discussion Survey')
    manager_discussion_survey = fields.Many2one('survey.survey',string = 'Manager Discussion Survey')
    final_discussion_survey = fields.Many2one('survey.survey',string = 'Final Discussion Survey')

    hr_response_id = fields.Many2one('survey.user_input', "HR Response", ondelete="set null", oldname="response")
    tech_response_id = fields.Many2one('survey.user_input', "Technical Response", ondelete="set null", oldname="response")
    man_response_id = fields.Many2one('survey.user_input', "Manager Response", ondelete="set null", oldname="response")
    final_response_id = fields.Many2one('survey.user_input', "Final Response", ondelete="set null", oldname="response")
    signature_item_id = fields.Many2one('signature.request',string='signature request')
    salary_proposed = fields.Char("Proposed Salary", group_operator="avg", help="Salary Proposed by the Organisation")
    salary_expected = fields.Char("Expected Salary", group_operator="avg", help="Salary Expected by Applicant")

    @api.multi
    def write(self, vals):
        # user_id change: update date_open
        
        res = super(Applicant, self).write(vals)

        print (vals.get('stage_id'))

        if vals.get('stage_id'):

            stage_obj = self.env['hr.recruitment.stage'].search([('id' , '=' , int(vals.get('stage_id')))])

            if stage_obj.stage_code == 'SCD':
                self.hr_discussion_survey = stage_obj.survey_id
            elif stage_obj.stage_code == 'Th':
                self.tech_discussion_survey = stage_obj.survey_id
            elif stage_obj.stage_code == 'Mg':
                self.manager_discussion_survey = stage_obj.survey_id
            elif stage_obj.stage_code == 'FD':
                self.final_discussion_survey = stage_obj.survey_id

            # self.survey_id = stage_obj.survey_id

        return res

    @api.multi
    def action_hr_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.hr_response_id:
            response = self.env['survey.user_input'].create({'survey_id': self.hr_discussion_survey.id, 'partner_id': self.partner_id.id})
            self.hr_response_id = response.id
        else:
            response = self.hr_response_id
        self.survey_id.applicant_id = self.id
        print('self.survey_id.applicant_id',self.survey_id.applicant_id)
        # grab the token of the response and start surveying
        return self.survey_id.with_context(survey_token=response.token).action_start_survey()

    @api.multi
    def action_hr_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.hr_response_id:
            self.hr_discussion_survey.applicant_id = self.id
            return self.hr_discussion_survey.action_print_survey()
        else:
            response = self.hr_response_id
            self.hr_discussion_survey.applicant_id = self.id
            return self.hr_discussion_survey.with_context(survey_token=response.token).action_print_survey()

    @api.multi
    def action_tech_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.tech_response_id:
            response = self.env['survey.user_input'].create({'survey_id': self.tech_discussion_survey.id, 'partner_id': self.partner_id.id})
            self.tech_response_id = response.id

        else:
            response = self.tech_response_id
            
        self.survey_id.applicant_id = self.id
        # grab the token of the response and start surveying
        return self.survey_id.with_context(survey_token=response.token).action_start_survey()

    @api.multi
    def action_tech_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.tech_response_id:
            self.tech_discussion_survey.applicant_id = self.id
            return self.tech_discussion_survey.action_print_survey()
        else:
            self.tech_discussion_survey.applicant_id = self.id
            response = self.tech_response_id
            return self.tech_discussion_survey.with_context(survey_token=response.token).action_print_survey()

    @api.multi
    def action_manager_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.man_response_id:
            response = self.env['survey.user_input'].create({'survey_id': self.manager_discussion_survey.id, 'partner_id': self.partner_id.id})
            self.man_response_id = response.id
        else:
            response = self.man_response_id
        # grab the token of the response and start surveying
        self.survey_id.applicant_id = self.id
        return self.survey_id.with_context(survey_token=response.token).action_start_survey()

    @api.multi
    def action_manager_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.man_response_id:
            self.manager_discussion_survey.applicant_id = self.id
            return self.manager_discussion_survey.action_print_survey()
        else:
            response = self.man_response_id
            self.manager_discussion_survey.applicant_id = self.id
            return self.manager_discussion_survey.with_context(survey_token=response.token).action_print_survey()

    @api.multi
    def action_final_start_survey(self):
        self.ensure_one()
        # create a response and link it to this applicant
        if not self.final_response_id:
            response = self.env['survey.user_input'].create({'survey_id': self.final_discussion_survey.id, 'partner_id': self.partner_id.id})
            self.final_response_id = response.id
        else:
            response = self.final_response_id
        # grab the token of the response and start surveying
        self.survey_id.applicant_id = self.id
        return self.survey_id.with_context(survey_token=response.token).action_start_survey()

    @api.multi
    def action_final_print_survey(self):
        """ If response is available then print this response otherwise print survey form (print template of the survey) """
        self.ensure_one()
        if not self.final_response_id:
            self.final_discussion_survey.applicant_id = self.id
            return self.final_discussion_survey.action_print_survey()
        else:
            response = self.final_response_id
            self.final_discussion_survey.applicant_id = self.id
            return self.final_discussion_survey.with_context(survey_token=response.token).action_print_survey()


    @api.multi
    @api.depends('stage_id')
    def _stage_change_flag(self):

        for rec in self:
            if rec.stage_id.stage_code == 'OF':
                rec.stage_change_flag = 'offer'
            elif rec.stage_id.stage_code == 'Th':
                rec.stage_change_flag = 'tech'
            elif rec.stage_id.stage_code == 'Mg':
                rec.stage_change_flag = 'man'
            elif rec.stage_id.stage_code == 'FD':
                rec.stage_change_flag = 'final'
            elif rec.stage_id.stage_code == 'New':
                rec.stage_change_flag = 'new'
            elif rec.stage_id.stage_code == 'SCD':
                rec.stage_change_flag = 'scheduled'
            else:
                rec.stage_change_flag = ''



    @api.model
    def get_from_email(self):
        alias_name = self.env.ref('ppts_recruitment_enhancement.mail_alias_recruitment_new').alias_name
        alias_domain = self.env["ir.config_parameter"].get_param("mail.catchall.domain")




    @api.multi
    def action_offer_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('ppts_recruitment_enhancement', 'email_template_data_offer_letter')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
 
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        mail_id={
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }  
        
        return mail_id
        
    @api.multi
    def action_tech_discussion_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('ppts_recruitment_enhancement', 'email_template_data_technical_discussion')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
 
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        mail_id={
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }  
        
        return mail_id
    
    @api.multi
    def send_launch_pack(self):
        if self.job_id.job_template.sign_document_id:
            if not self.signature_item_id:
                template_ids = []
                template_id = self.env['signature.request.template'].search([('id', '=',self.job_id.job_template.sign_document_id.id)])
               
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
                    if not self.partner_id:
                        applicant_name = str(self.partner_name or '') + ' ' + str(self.middlename or '') + ' ' + str(self.lastname or '')
                        partner = self.env['res.partner'].create({
                            'name':applicant_name,
                            'partner_name':applicant_name,
                            'email':self.email_from,
                            'phone':self.partner_phone or '',
                            'function':self.job_id.name or '',
                            'applicant_id':self.id or '',
                            'mobile':self.partner_mobile or ''
                            })
                        self.partner_id = partner.id
                    
                    if self.partner_id:
                        if template_id:
                            signers = []
                            signer = {}
                            for role in roles:
                                signer = {
                                'partner_id' : self.partner_id.id,
                                'role': role
                                }
                                signers.append(signer)
                            req_id = self.env["signature.request"].with_context({'template_id': template_ids, 'reference': template_ids, 'status':'launch'}).initialize_new(template_ids[0][0], signers, followers=[], reference=reference, subject="", message="", send=False)
                            self.signature_item_id = req_id['id']
            return self.signature_item_id
        else:
            raise ValidationError("Please Choose the CIF Document Template")
        

    @api.multi
    def action_applicant_schedule_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        
        doc_id = self.send_launch_pack()
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        link = url_join(base_url, "/jobs/apply/%(applicantid)s" % {'applicantid':self.id})
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('ppts_recruitment_enhancement', 'email_template_applicant_schedule')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_applicant': True,
            'link':link
        })
        mail_id={
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }  
        
        return mail_id
        
    @api.multi
    def action_manager_discussion_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('ppts_recruitment_enhancement', 'email_template_data_manager_discussion')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
 
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        mail_id={
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
        
        return mail_id
        
    @api.multi
    def action_final_discussion_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('ppts_recruitment_enhancement', 'email_template_data_final_discussion')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
 
        ctx.update({
            'default_model': 'hr.applicant',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        mail_id={
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }  
        
        return mail_id
    

#     @api.multi
#     def send_l1_tech_round(self):
#         self.l1_round = True
#         if self.stage_id:
#             if self.stage_id.stage_code == 'HRS':
#                 l1_stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','L1-R')]).id
#                 self.stage_id = l1_stage_id
# 
#     @api.multi
#     def send_l2_tech_round(self):
#         self.l2_round = True
#         if self.stage_id:
#             if self.stage_id.stage_code in ('L1-S','HRS'):
#                 l1_stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','L2-R')]).id
#                 self.stage_id = l1_stage_id
# 
#     @api.multi
#     def send_manager_round(self):
#         self.manager = True
#         if self.stage_id:
#             if self.stage_id.stage_code in ( 'L2-S','L1-S','HRS'):
#                 l1_stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','MR-R')]).id
#                 self.stage_id = l1_stage_id
#         
#     @api.multi
#     def send_final_discussion(self):
#         if self.stage_id:
#             if self.stage_id.stage_code == 'MR-S':
#                 l1_stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','FD')]).id
#                 self.stage_id = l1_stage_id
    
    
#     @api.multi
#     def approve1(self):
#         if self.stage_id:
#             if self.stage_id.stage_code == 'L1-R':
#                 l1_stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','L1-S')]).id
#                 self.stage_id = l1_stage_id
#         
#     @api.multi
#     def approve2(self):
#         if self.stage_id:
#             if self.stage_id.stage_code == 'L2-R':
#                 l1_stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','L2-S')]).id
#                 self.stage_id = l1_stage_id
#                 
#                 
#     @api.multi
#     def approve3(self):
#         if self.stage_id:
#             if self.stage_id.stage_code == 'MR-R':
#                 l1_stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','MR-S')]).id
#                 self.stage_id = l1_stage_id
    @api.multi
    def send_offer_letter(self):
        if self.stage_id:
            if self.stage_id.stage_code == 'FD':
                l1_stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','OL')]).id
                self.stage_id = l1_stage_id
                
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        url = self.stage_id.survey_id.public_url
        url = urls.url_parse(url).path[1:]
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        try:
            template_id = ir_model_data.get_object_reference('ppts_recruitment_enhancement', 'email_template_data_offer_letter_applicant')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        
        ctx.update({
            'default_model': 'hr.applicant',
            'default_partner_ids': user.partner_id.ids,
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_partner_name': self.partner_name,
#             'custom_layout': "ppts_recruitment_enhancement.email_template_data_offer_letter_applicant",
        })
        mail_id = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }  
        
        
        return mail_id
#     @api.multi
#     def onboarding(self):
#         if self.stage_id:
#             if self.stage_id.stage_code == 'OL':
#                 l1_stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','OB')]).id
#                 self.stage_id = l1_stage_id
                
                

    
    
class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'

    applicant = fields.Boolean('Applicant')
    activity_type_id = fields.Many2one('mail.activity.type','Activity')
    schedule_date = fields.Date('Date')
    
    @api.onchange('activity_type_id','schedule_date')
    def onchange_activity_type_id(self):
        for rec in self:
            
            if rec.schedule_date and rec.schedule_date:
                rec.subject = 'Scheduled for ' + rec.activity_type_id.name + ' on ' + rec.schedule_date
            elif rec.activity_type_id:
                rec.subject = 'Scheduled for ' + rec.activity_type_id.name
            elif rec.schedule_date:
                rec.subject = 'Scheduled ' + ' on ' + rec.schedule_date

    @api.multi
    def send_mail_action(self):
        # TDE/ ???
        if self.applicant == True:
            model_id = self.env['ir.model'].search([('model','=','hr.applicant')])
            applicant_ids = self.env['hr.applicant'].search([('id','=',self.res_id)])
            
            activity = self.env['mail.activity'].create({'res_id':self.res_id,
                                        'res_model_id': model_id.id,
                                        'activity_type_id': self.activity_type_id.id,
                                        'summary': self.subject,
                                        'res_model': model_id.model,
                                        'res_name': applicant_ids.name,
                                        'date_deadline': self.schedule_date,
                                        'user_id': self.env.uid,
                                        })

        return self.send_mail()

    @api.multi
    def send_mail(self, auto_commit=False):
        """ Process the wizard content and proceed with sending the related
            email(s), rendering any template patterns on the fly if needed. """
        for wizard in self:
            # Duplicate attachments linked to the email.template.
            # Indeed, basic mail.compose.message wizard duplicates attachments in mass
            # mailing mode. But in 'single post' mode, attachments of an email template
            # also have to be duplicated to avoid changing their ownership.
            if wizard.attachment_ids and wizard.composition_mode != 'mass_mail' and wizard.template_id:
                new_attachment_ids = []
                for attachment in wizard.attachment_ids:
                    if attachment in wizard.template_id.attachment_ids:
                        new_attachment_ids.append(attachment.copy({'res_model': 'mail.compose.message', 'res_id': wizard.id}).id)
                    else:
                        new_attachment_ids.append(attachment.id)
                    wizard.write({'attachment_ids': [(6, 0, new_attachment_ids)]})

            # Mass Mailing
            mass_mode = wizard.composition_mode in ('mass_mail', 'mass_post')

            Mail = self.env['mail.mail']
            ActiveModel = self.env[wizard.model if wizard.model else 'mail.thread']
            if wizard.template_id:
                # template user_signature is added when generating body_html
                # mass mailing: use template auto_delete value -> note, for emails mass mailing only
                Mail = Mail.with_context(mail_notify_user_signature=False)
                ActiveModel = ActiveModel.with_context(mail_notify_user_signature=False, mail_auto_delete=wizard.template_id.auto_delete)
            if not hasattr(ActiveModel, 'message_post'):
                ActiveModel = self.env['mail.thread'].with_context(thread_model=wizard.model)
            if wizard.composition_mode == 'mass_post':
                # do not send emails directly but use the queue instead
                # add context key to avoid subscribing the author
                ActiveModel = ActiveModel.with_context(mail_notify_force_send=False, mail_create_nosubscribe=True)
            # wizard works in batch mode: [res_id] or active_ids or active_domain
            if mass_mode and wizard.use_active_domain and wizard.model:
                res_ids = self.env[wizard.model].search(safe_eval(wizard.active_domain)).ids
            elif mass_mode and wizard.model and self._context.get('active_ids'):
                res_ids = self._context['active_ids']
            else:
                res_ids = [wizard.res_id]

            batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
            sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]

            if wizard.composition_mode == 'mass_mail' or wizard.is_log or (wizard.composition_mode == 'mass_post' and not wizard.notify):  # log a note: subtype is False
                subtype_id = False
            elif wizard.subtype_id:
                subtype_id = wizard.subtype_id.id
            else:
                subtype_id = self.sudo().env.ref('mail.mt_comment', raise_if_not_found=False).id

            for res_ids in sliced_res_ids:
                batch_mails = Mail
                all_mail_values = wizard.get_mail_values(res_ids)
                for res_id, mail_values in all_mail_values.items():
                    if wizard.composition_mode == 'mass_mail':
                        batch_mails |= Mail.create(mail_values)
                    else:
                        ActiveModel.browse(res_id).message_post(
                            message_type=wizard.message_type,
                            subtype_id=subtype_id,
                            **mail_values)

                if wizard.composition_mode == 'mass_mail':
                    batch_mails.send(auto_commit=auto_commit)

        return {'type': 'ir.actions.act_window_close'}
 
 
class HrLanguageLine(models.Model):
    _name = 'hr.language.line'
     
    name = fields.Char(string='Name')
     
class ApplicantLanguageLineItem(models.Model):
    _name = 'applicant.lang.item'
      
    lang_id = fields.Many2one("hr.language.line", string="Language",required=True)
    check_box1 = fields.Boolean(string='Speak')
    check_box2 = fields.Boolean(string='Read')
    check_box3 = fields.Boolean(string='Write')
    app_lang_id = fields.Many2one("hr.applicant", string="Lang")
 
 
class ApplicantDetailItem(models.Model):
    _name = 'applicant.details.item'
      
    name = fields.Char(string='Name',required=True)
    relationship_applicant = fields.Char(string='Relationship',required=True)
    date = fields.Date(string='Date of Birth')
    occupation = fields.Char(string='Occupation')
    annual_income = fields.Char(string='Annual Income')
    applicant_detail_id = fields.Many2one("hr.applicant", string="Details")
 
 
 
class ApplicantReferenceDetails(models.Model):
    _name = 'applicant.reference.details'
      
    name = fields.Char(string='Name')
    relationship_app = fields.Text(string='Relationship')
    no_years = fields.Char(string='No. of years known')
    occupation = fields.Char(string='Occupation')
    address_details = fields.Char(string='Email ID')
    phone_no = fields.Char(string='Phone Number')
    applicant_reference_id = fields.Many2one("hr.applicant", string="Details")
  
 
 
class ApplicantWorkDetails(models.Model):
    _name = 'applicant.work.details'
      
    doc_name = fields.Char(string='Particulars')
    last_job = fields.Char(string='Last Job / Present Job')
    present_job = fields.Char(string='Present Job')
    second_job = fields.Char(string='Second Job / Last Job')
    sec_last_job = fields.Char(string='Last Job')
    third_job = fields.Char(string='Third Job / Last Job')
    th_last_job = fields.Char(string='Last Job')
    fourth_job = fields.Char(string='Fourth Job / Last Job')
    four_last_job = fields.Char(string='Last Job')
    fifth_job = fields.Char(string='Fifth Job / Last Job')
    fif_last_job = fields.Char(string='Last Job')   
    applicant_work_id = fields.Many2one("hr.applicant", string="Work Details")
  
  
 
 
 
        
        