# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.exceptions import UserError, ValidationError
import re
import pytz, datetime
from datetime import datetime, date, timedelta
experience_year = []
for year in range(0, 11):
    experience_year.append((str(year), str(year)))
from werkzeug import urls

class CalenderEvent(models.Model):
    _inherit = 'calendar.event'
    
    email_from = fields.Char("email")
    
    @api.model
    def get_from_email(self):
        alias_name = self.env.ref('ppts_recruitment_enhancement.mail_alias_recruitment_new').alias_name
        alias_domain = self.env["ir.config_parameter"].get_param("mail.catchall.domain")
#         return alias_name+"@"+alias_domain

    @api.multi
    def send_offer_letter(self):        
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        date_t = datetime.strptime(str(self.start_datetime), '%Y-%m-%d %H:%M:%S')
        local = pytz.timezone ("America/Los_Angeles")
        naive = datetime.strptime (str(self.start_datetime), "%Y-%m-%d %H:%M:%S")
        local_dt = local.localize(naive, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        start_date = utc_dt.strftime ("%Y-%m-%d %H:%M:%S")
        test = datetime.strptime (str(start_date), "%Y-%m-%d %H:%M:%S")
        final_date = test - timedelta(hours=2, minutes=30)
        
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        try:
            template_id = ir_model_data.get_object_reference('ppts_recruitment_enhancement', 'email_template_data_offer_letter_employee')[1]
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
             'diff_days' : final_date,
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

    
class MailComposer(models.TransientModel):
    _inherit = 'mail.compose.message'
    
    @api.multi
    def send_mail_action(self):
        # TDE/ ???
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

    
class ApplicantQualificationLine(models.Model):
    _name = 'applicant.qualification.line'
    
    name = fields.Char(string='Name')
    code = fields.Char(string='code')

    
class ApplicantQualificationLineItem(models.Model):
    _name = 'applicant.qualification.item'
    
    name = fields.Many2one("hr.qualification.line", string="Name")
    code = fields.Char(related='name.code', string='code')
    
    qualification_id = fields.Many2one("hr.applicant", string="Qualification")


class ApplicantKeyskillsLine(models.Model):
    _name = 'applicant.keyskills.line'
    
    name = fields.Char(string='Name')
    code = fields.Char(string='code')

    
class ApplicantKeyskillsLineItem(models.Model):
    _name = 'applicant.keyskills.item'
    
    name = fields.Many2one("hr.keyskills.line", string="Name", required=True)
    code = fields.Char(related='name.code', string='code')
    
    keyskills_id = fields.Many2one("hr.applicant", string="Key Skills & Abilities")


class Applicant(models.Model):
    _inherit = "hr.applicant"

    tot_exp = fields.Selection([('fresher', 'Fresher'),
                                ('below1', 'Below 1 Year'), 
                                ('1to2', '1-2 Years'), 
                                ('2to4', '2-4 Years'), 
                                ('4to6', '4-6 Years'), 
                                ('6above', 'Above 6 Years')],string="Total Experience")
    applicant_qualification = fields.Many2one('hr.qualification.line', string='Applicant Qualification')
    current_company = fields.Char('Current Company')
    current_location = fields.Char('Current Location')
    relevant_exp = fields.Float("Relevant Experience")
    notice_period = fields.Float("Notice Period")
    
    partner_name = fields.Char("First Name", required=True)
#     last_name = fields.Char("Last Name",required=True)
#     middle_name = fields.Char("Middle Name")
    exp_in_yr = fields.Selection(experience_year, string="Experience in Year")
    exp_in_month = fields.Selection(experience_year, string="To")
    age_preference = fields.Selection([('21_to_30', '21 - 30'), ('31_to_40', '31 - 40'), ('40_above', 'Above 40')])
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')])
    reason_for_manpower = fields.Many2one('reason.manpower')
    type = fields.Selection([('contract', 'Contract'), ('permanent', 'Permanent')], string='Type')
    contract_month = fields.Selection(experience_year, string="Contract Months")
    budget_from = fields.Integer(string='Budget')
    budget_to = fields.Integer(string='to')
#     reason_for_cancel = fields.Char(string='Reason for Cancel',readonly=True)
    actual_qualification_ids = fields.Many2many('hr.qualification.line', string='Qualification')
    actual_keyskill_ids = fields.Many2many('hr.keyskills.line', string='Key Skills& Abilities')
    job_description = fields.Text(string='Job Description')
    
    applicant_qualification_ids = fields.One2many("applicant.qualification.item", "qualification_id", string="Qualification")

    applicant_keyskills_ids = fields.One2many("applicant.keyskills.item", "keyskills_id", string="Key Skills & Abilities")
    
    sequence_id = fields.Char('Sequence', readonly=True)
    
    @api.onchange('job_id')
    def onchange_job_id(self):
        vals = self._onchange_job_id_internal(self.job_id.id)
        self.department_id = vals['value']['department_id']
        self.user_id = vals['value']['user_id']
        self.stage_id = vals['value']['stage_id']
        
        job = self.env['hr.job'].browse(self.job_id.id)
        self.exp_in_yr = job.exp_in_yr
        self.exp_in_month = job.exp_in_month
        self.age_preference = job.age_preference
        self.gender = job.gender
        self.reason_for_manpower = job.reason_for_manpower
#         self.type = job.type
#         self.contract_month = job.contract_month
        self.budget_from = job.budget_from
        self.budget_to = job.budget_to
        self.job_description = job.description
        if job.hr_qualification_ids:
            qualification_lines = []
            for line in job.hr_qualification_ids:

                line_vals = {
                    'name': line.name,
                    'code': line.code,
                }
                
                qualification_lines.append((0, 0, line_vals))

            self.update({'applicant_qualification_ids':qualification_lines})
        else:
            self.applicant_qualification_ids.unlink()
            
        if job.hr_keyskills_ids:
            keyskills_lines = []
            for line in job.hr_keyskills_ids:

                line_val = {
                    'name': line.name,
                    'code': line.code,
                }
                
                keyskills_lines.append((0, 0, line_val))

            self.update({'applicant_keyskills_ids':keyskills_lines})
        else:
            self.applicant_keyskills_ids.unlink()

#         if job.hr_keyskills_ids:
#             self.applicant_keyskills_ids = job.hr_keyskills_ids
        
    @api.constrains('email_from')
    def validate_email(self):
        for obj in self:
            if obj.email_from:
                if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", obj.email_from) == None:
                    raise ValidationError("Please Provide valid Email Address: %s" % obj.email_from)
            if not obj.email_from:
                raise ValidationError(
                    _('Please Enter Email'),
                )

    @api.model
    def create(self, vals):
#         created sequence
        seq = self.env['ir.sequence'].next_by_code('hr.applicant') or '/'
        stage_id = self.env['hr.recruitment.stage'].search([('stage_code','=','New')])
        if vals['department_id']:
            dept = self.env['hr.department'].browse(vals['department_id'])
            curnt_date = date.today()
            dept_name = ''
            if dept.parent_id.name:
                dept_name = dept.parent_id.name
            else:
                dept_name = dept.name
            seq_concat = 'PPTS/' + dept_name + '-REC/' + seq + '/' + curnt_date.strftime('%m') + '/' + curnt_date.strftime('%y')
        else:
            seq_concat = 'AP/' + seq
        vals['sequence_id'] = seq_concat
        vals['stage_id'] = stage_id.id
        if vals.get('email_from'):
            email_id = self.env['hr.applicant'].search([('email_from', '=', vals.get('email_from'))])
            if email_id:
                raise ValidationError(
                    _('Email name must be unique!'),
                )
        return super(Applicant, self).create(vals) 
            
    @api.multi
    def write(self, vals):
        context = dict(self.env.context or {})
        if vals.get('email_from'):
            email_id = self.env['hr.applicant'].search([('email_from', '=', vals.get('email_from'))])
            if email_id:
                raise ValidationError(
                    _('Email name must be unique!'),
                )
        if vals.get('stage_id'):
            stage_id = self.env['hr.recruitment.stage'].search([('id','=',vals.get('stage_id'))])
            survey_template_id = self.env.ref('ppts_recruitment_enhancement.applicant_email_template_survey')
            print(survey_template_id)
            if stage_id.template_id or stage_id.survey_id :
                if stage_id.stage_code =='Th':
                    if stage_id.survey_id:
                        url = stage_id.survey_id.public_url
                        url = urls.url_parse(url).path[1:]
                        print(url)
                        context['survey_url'] = url
                        survey_template_id.with_context(context).send_mail(self.id, force_send=True)
#                     stage_id.template_id.with_context(context).send_mail(self.id, force_send=True)
                elif stage_id.stage_code == 'NEW':
                    stage_id.template_id.with_context(context).send_mail(self.id, force_send=True)
                elif stage_id.stage_code == 'MG':     
                    if stage_id.survey_id:
                        url = stage_id.survey_id.public_url
                        url = urls.url_parse(url).path[1:]
                        context['survey_url'] = url
                        print(url,'mg')
                        survey_template_id.with_context(context).send_mail(self.id, force_send=True)
#                     stage_id.template_id.with_context(context).send_mail(self.id, force_send=True)
                    
                elif stage_id.stage_code == 'FD':   
                    if stage_id.survey_id:
                        url = stage_id.survey_id.public_url
                        url = urls.url_parse(url).path[1:]
                        context['survey_url'] = url
                        survey_template_id.with_context(context).send_mail(self.id, force_send=True)
                    # stage_id.template_id.with_context(context).send_mail(self.id, force_send=True)
        return super(Applicant, self).write(vals)
    
    @api.multi
    def action_makeMeeting(self):
        """ This opens Meeting's calendar view to schedule meeting on current applicant
            @return: Dictionary value for created Meeting view
        """
        self.ensure_one()
        partners = self.partner_id | self.user_id.partner_id | self.department_id.manager_id.user_id.partner_id

        category = self.env.ref('hr_recruitment.categ_meet_interview')
        res = self.env['ir.actions.act_window'].for_xml_id('calendar', 'action_calendar_event')
        res['context'] = {
            'search_default_partner_ids': self.partner_id.name,
            'default_partner_ids': partners.ids,
            'default_user_id': self.env.uid,
            'default_name': self.name,
            'default_email_from': self.email_from,
            'default_categ_ids': category and [category.id] or False,
        }
        return res

    
class ReasonManpower(models.Model):
    _name = 'reason.manpower'
    name = fields.Char(string='Name')
    code = fields.Char(string='code')


class HrQualificationLine(models.Model):
    _name = 'hr.qualification.line'
    
    name = fields.Char(string='Name')
    code = fields.Char(string='code')

    
class HrQualificationLineItem(models.Model):
    _name = 'hr.qualification.item'
    
    name = fields.Many2one("hr.qualification.line", string="Name", required=True)
    code = fields.Char(related='name.code', string='code')
    
    qualification_id = fields.Many2one("hr.job", string="Qualification")
    hr_position_log_id = fields.Many2one('hr.job.position.log', string="HR Position Log")


class HrKeyskillsLine(models.Model):
    _name = 'hr.keyskills.line'
    
    name = fields.Char(string='Name')
    code = fields.Char(string='code')

    
class HrKeyskillsLineItem(models.Model):
    _name = 'hr.keyskills.item'
    
    name = fields.Many2one("hr.keyskills.line", string="Name", required=True)
    code = fields.Char(related='name.code', string='code')
    
    keyskills_id = fields.Many2one("hr.job", string="Key Skills & Abilities")
    hr_position_log_id = fields.Many2one('hr.job.position.log', string="HR Position Log")

    
class HrJob(models.Model):
    _inherit = ['hr.job']

    state = fields.Selection([
        ('draft', 'Draft'),
#         ('first_approval', 'Waiting for First Approval'),
        ('approval', 'Waiting for Approval'),
#         ('approved', 'Approved'),
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting'),
        ('refuse', 'Refuse')
    ], string='Status', readonly=True, required=True, track_visibility='always', copy=False, default='draft', help="Set whether the recruitment process is open or closed for this job position.")
    
    job_type = fields.Many2one('hr.contract.type', string="Job Type")
    job_seniority_id = fields.Many2one('hr.job.seniority.title', string="Job seniority title")
    job_seniority_value = fields.Many2many("hr.job.seniority.title", string="Job Domain")
    job_template = fields.Many2one("hr.job.template", string="Job Template", required=True)
    application_survey_id = fields.Many2one("survey.survey", string="Applicant Survey")
    introduction = fields.Text(string="Introduction", help="Provide a brief introduction to the position.  Some users use this space to introduce their company to the candidate.")
    introduction_box = fields.Boolean()
    description_box = fields.Boolean()
    hide_first_approval = fields.Boolean(string='Hide First Approval')
    hide_second_approval = fields.Boolean(string='Hide Second Approval')
    hide_third_approval = fields.Boolean(string='Hide Third Approval')
    hide_approved = fields.Boolean(string='Hide Approved')
    exp_in_yr = fields.Selection(experience_year, string="Experience in Year")
    exp_in_month = fields.Selection(experience_year, string="To")
    age_preference = fields.Selection([('21_to_30', '21 - 30'), ('31_to_40', '31 - 40'), ('40_above', 'Above 40')])
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')])
    reason_for_manpower = fields.Many2one('reason.manpower')
#     type = fields.Selection([('contract', 'Contract'), ('permanent', 'Permanent')], string='Type', default='permanent')
#     contract_month = fields.Selection(experience_year, string="Contract Months")
    budget_from = fields.Integer(string='Budget')
    budget_to = fields.Integer(string='to')
    reason_for_cancel = fields.Char(string='Reason for Cancel', readonly=True)
    
    hr_qualification_ids = fields.One2many("hr.qualification.item", "qualification_id", string="Qualification")

    hr_keyskills_ids = fields.One2many("hr.keyskills.item", "keyskills_id", string="Key Skills & Abilities")
    
    sequence_id = fields.Char('Sequence', readonly=True)
    expected_date = fields.Date("Expected Date")
    recruitment_date = fields.Date("Date")
    closed_date = fields.Date("Closed Date")
    hr_position_log_ids = fields.One2many("hr.job.position.log", "hr_job_id")
    mprf_job_position_ids = fields.One2many('mprf.request','mprf_job_position_id', string = 'MPRF Request Ref')
    
    @api.multi
    def action_print_applicant_survey(self):
        return self.application_survey_id.action_print_survey()
    
#     @api.multi
#     def first_approval(self):
#         self.state = 'first_approval'
#         self.hide_first_approval = True
#         seq = self.env['ir.sequence'].next_by_code('hr.job') or '/'
#         self.sequence_id = seq
    @api.multi
    def approval(self):
        self.hide_second_approval = True
        if self.state == 'draft':
            self.state = 'approval'
            seq = self.env['ir.sequence'].next_by_code('hr.job') or '/'
            self.sequence_id = seq
        else :
            self.state = 'draft'

    @api.multi
    def recruitment_progress(self):
        self.hide_third_approval = True
        if self.state == 'approval':
            self.state = 'recruit'
            self.recruitment_date = datetime.date(datetime.now())
            
        else :
            self.state = 'approval'
            
    @api.onchange('job_template')
    def onchange_job_template(self):
        if self.job_template:
            self.application_survey_id = self.job_template.application_survey_id.id
            self.survey_id = self.job_template.interviewer_survey_id.id
            self.description = self.job_template.job_description
            self.introduction = self.job_template.introduction
            self.department_id = self.job_template.department_id.id
            res = {'domain': {
            'job_seniority_id': "[('id', '!=', False)]",
            }}
            jrl_ids = []
            for line in self.job_template.job_seniority_id:
                jrl_ids.append(line.id)
            res['domain']['job_seniority_id'] = "[('id', 'in', %s)]" % jrl_ids
            return res
    @api.multi
    def set_open(self):
        return self.write({
            'state': 'open',
            'no_of_recruitment': 0,
            'no_of_hired_employee': 0,
            'closed_date':datetime.date(datetime.now())
        })  
    
    @api.multi
    def set_recruit(self):
        for record in self:
            duration = 0
            if record.closed_date and record.recruitment_date:
                duration = (datetime.strptime(record.closed_date, "%Y-%m-%d")-datetime.strptime(record.recruitment_date, "%Y-%m-%d")).days
            print(record.id)    
            log_id = self.env['hr.job.position.log'].create({'job_type':record.job_type.id,
                                                             'job_seniority_id':record.job_seniority_id.id,
                                                             'name':record.name,
                                                             'job_template':record.job_template.id,
                                                             'department_id':record.department_id.id,
                                                             'survey_id':record.survey_id.id,
                                                             'application_survey_id':record.application_survey_id.id,
                                                             'address_id':record.address_id.id,
                                                             'user_id':record.user_id.id,
                                                             'no_of_recruitment':record.no_of_recruitment,
                                                             'hr_responsible_id':record.hr_responsible_id.id,
                                                             'exp_in_yr':record.exp_in_yr,
                                                             'exp_in_month':record.exp_in_month,
                                                             'age_preference':record.age_preference,
                                                             'gender':record.gender,
                                                             'reason_for_manpower':record.reason_for_manpower.id,
                                                             'budget_from':record.budget_from,
                                                             'budget_to':record.budget_to,
                                                             'expected_date':record.expected_date,
                                                             'recruitment_date':record.recruitment_date,
                                                             'closed_date':record.closed_date,
                                                             'hr_job_id':record.id,
                                                             'sequence_id':record.sequence_id,
                                                             'intro':record.introduction,
                                                             'intro_box':record.introduction_box,
                                                             'descript':record.description,
                                                             'descript_box':record.description_box,
                                                             'duration_days':duration or 0
                                                                 })
            if log_id:                   
                print(log_id)
                for qual_lines in record.hr_qualification_ids:
                    qual_lines.write({'hr_position_log_id':log_id.id})
                for keys_lines in record.hr_keyskills_ids:
                    keys_lines.write({'hr_position_log_id':log_id.id})    
#             seq = self.env['ir.sequence'].next_by_code('hr.job') or '/'
            no_of_recruitment = 1 if record.no_of_recruitment == 0 else record.no_of_recruitment
            record.write({'state': 'draft', 'no_of_recruitment': no_of_recruitment, 'closed_date':None, 'sequence_id':None, 'recruitment_date':datetime.date(datetime.now()),'expected_date':None})
            return True   

    def action_get_mprf_request_view(self):

        tree_id = self.env.ref('ppts_recruitment_enhancement.mprf_request_tree').id
        form_id = self.env.ref('ppts_recruitment_enhancement.mprf_request_form').id

        mprf_obj = self.env['mprf.request'].search([('job_position_id' , '=' , self.id)])

        return{
            'name': _('MPRF Request'),
            'type':'ir.actions.act_window',
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model':'mprf.request',
            'domain' : [('id', '=', mprf_obj.ids)],
            'views_id':False,
            'views':[(tree_id or False, 'tree'), (form_id or False, 'form')],
            }

    
class JobPositionLog(models.Model):
    _name = 'hr.job.position.log'
    
    job_type = fields.Many2one('hr.contract.type', string="Job Type")
    job_seniority_id = fields.Many2one('hr.job.seniority.title', string="Job seniority title")
    job_seniority_value = fields.Many2many("hr.job.seniority.title", string="Job Domain")
    job_template = fields.Many2one("hr.job.template", string="Job Template", required=True)
    application_survey_id = fields.Many2one("survey.survey", string="Applicant Survey")
    intro = fields.Text(string="Introduction", help="Provide a brief introduction to the position.  Some users use this space to introduce their company to the candidate.")
    intro_box = fields.Boolean()
    descript_box = fields.Boolean()
    hide_first_approval = fields.Boolean(string='Hide First Approval')
    hide_second_approval = fields.Boolean(string='Hide Second Approval')
    hide_third_approval = fields.Boolean(string='Hide Third Approval')
    hide_approved = fields.Boolean(string='Hide Approved')
    exp_in_yr = fields.Selection(experience_year, string="Experience in Year")
    exp_in_month = fields.Selection(experience_year, string="To")
    age_preference = fields.Selection([('21_to_30', '21 - 30'), ('31_to_40', '31 - 40'), ('40_above', 'Above 40')])
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')])
    reason_for_manpower = fields.Many2one('reason.manpower')
#     type = fields.Selection([('contract', 'Contract'), ('permanent', 'Permanent')], string='Type', default='permanent')
#     contract_month = fields.Selection(experience_year, string="Contract Months")
    budget_from = fields.Integer(string='Budget')
    budget_to = fields.Integer(string='to')
    reason_for_cancel = fields.Char(string='Reason for Cancel', readonly=True)
    
    hr_qualification_ids = fields.One2many("hr.qualification.item", "qualification_id", string="Qualification")

    hr_keyskills_ids = fields.One2many("hr.keyskills.item", "keyskills_id", string="Key Skills & Abilities")
    
    sequence_id = fields.Char('Sequence', readonly=True)
    expected_date = fields.Date("Expected Date")
    recruitment_date = fields.Date("Date")
    closed_date = fields.Date("Closed Date")
    department_id = fields.Many2one('hr.department', string='Department')
    address_id = fields.Many2one(
        'res.partner', "Job Location",
        help="Address where employees are working")   
    user_id = fields.Many2one('res.users', "Recruitment Responsible", track_visibility='onchange')
    no_of_recruitment = fields.Integer(string='Expected New Employees', copy=False,
        help='Number of new employees you expect to recruit.')
    hr_responsible_id = fields.Many2one('res.users', "HR Responsible", track_visibility='onchange',
        help="Person responsible of validating the employee's contracts.")
    hr_qualification_ids = fields.One2many("hr.qualification.item", "hr_position_log_id", string="Qualification")
    hr_keyskills_ids = fields.One2many("hr.keyskills.item", "hr_position_log_id", string="Key Skills & Abilities")
    hr_job_id = fields.Many2one("hr.job", string="Hr Job")        
    survey_id = fields.Many2one(
        'survey.survey', "Interview Form",
        help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job")
    name = fields.Char(string='Job Position', required=True, index=True, translate=True)
    descript = fields.Text(string='Job Description')
    duration_days = fields.Integer("Duration Days")
    


class MprfRequest(models.Model):
    _name = "mprf.request"
    _rec_name = 'job_position_id'

    department_id = fields.Many2one('hr.department',string = 'Department')
    num_of_positions = fields.Integer('Number of Positions')
    job_position_id = fields.Many2one('hr.job',string = 'Job Position')
    job_title_id = fields.Many2one('hr.job.seniority.title',string = 'Job Title')
    tentative_doj = fields.Date('Tentative DOJ')
    from_exp = fields.Selection(experience_year, string="Experience(in Year)")
    to_exp = fields.Selection(experience_year, string="To")
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ('others', 'Others')], string = 'Gender')
    manpower_reason = fields.Many2one('reason.manpower', string = 'Reason for Manpower')
    skills_required = fields.Many2many('hr.keyskills.line', string = 'Key Skills/Abilities')
    qualification_required = fields.Many2many('hr.qualification.line', string = 'Qualification')
    other_skills = fields.Char('Other skills,if any')
    reporting_to = fields.Many2one('hr.employee', string = 'Reporting To')
    budget_from = fields.Char('Budget(in CTC/years)')
    budget_to = fields.Char('To')
    employement_type = fields.Many2one('hr.contract.type', string = 'Employement Type')
    period_count = fields.Selection(experience_year, string = 'T/P/C Period')
    period_type = fields.Selection([('month', 'Months'), ('years', 'Years')])
    requested_by = fields.Many2one('hr.employee', string = 'Requested By')
    designation = fields.Many2one('hr.job.seniority.title',string = 'Designation')
    requested_date = fields.Date('Requested Date')
    job_description = fields.Text('Job Description')
    close_date = fields.Date('Close Date')
    duration_days = fields.Integer('Duration Days')
    status = fields.Selection([('new','New'),
                               ('requested','Requested'),
                               ('approved','Approved'),
                               ('close','Closed'),
                               ('rejected','Rejected')],default = 'new', string = 'Status')
    mprf_job_position_id = fields.Many2one('hr.job', string = 'Job Position Ref')

    def send_approval(self):
        self.status = 'requested'

    def approval_request(self):
        if self.mprf_job_position_id.state == 'draft':
            self.mprf_job_position_id.no_of_recruitment = self.num_of_positions
            self.mprf_job_position_id.state = 'recruit'
        else:
            self.mprf_job_position_id.no_of_recruitment = self.mprf_job_position_id.no_of_recruitment+self.num_of_positions
        self.status = 'approved'

    def close_request(self):
        self.close_date = datetime.now().date()
        print(self.create_date)
        self.duration_days = (datetime.strptime(self.close_date, "%Y-%m-%d")-datetime.strptime(self.requested_date, "%Y-%m-%d")).days
        self.status = 'close'

    def reject_request(self):
        self.status = 'rejected'

    

