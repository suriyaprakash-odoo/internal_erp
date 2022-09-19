import base64
import json
import pytz

from datetime import datetime
from psycopg2 import IntegrityError

from urllib.parse import urljoin

from odoo import http
from odoo.http import request
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.base.ir.ir_qweb.fields import nl2br
# from recaptcha.client import captcha

from odoo.addons.http_routing.models.ir_http import slug
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment
from odoo.addons.survey.controllers.main import WebsiteSurvey
import re


class WebsiteHrRecruitment(WebsiteHrRecruitment):

    @http.route([
        '/jobs/apply/<model("hr.job"):job>',
        '/jobs/apply/<int:id>'
        ], type='http', auth="public", website=True)
    def jobs_apply(self, job=None, id=None, **kwargs):
        error = {}
        default = {}
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True)) 
        States = env['res.country.state']
 
        # List jobs available to current UID
        state_ids = States.sudo().search([('country_id' , '=' , 104)]).ids
        state = States.sudo().browse(state_ids)
        country = request.env['res.country'].sudo().search([])
        print(country)
        if 'website_hr_recruitment_error' in request.session:
            error = request.session.pop('website_hr_recruitment_error')
            default = request.session.pop('website_hr_recruitment_default')

        applicant_obj = request.env['hr.applicant'].sudo().browse([id])
        print (applicant_obj)
        return request.render("website_hr_recruitment.apply", {
            'job': job,
            'error': error,
            'default': default,
            'states': state,
            'country' : country,
            'applicant_obj' : applicant_obj,
        })


    @http.route('/jobs/detail/<model("hr.job"):job>', type='http', auth="public", website=True)
    def jobs_detail(self, job, **kwargs):

        jobs = request.env['hr.job'].sudo().search([('state', '=' , 'recruit')])
        qualification = request.env['hr.qualification.line'].sudo().search([])

        return request.render("website_hr_recruitment.detail", {
            'jobs' : jobs,
            'qualification' : qualification,
            'job': job,
            'main_object': job,
        })

    @http.route("/job-apply", type='http', auth="public", website=True, csrf=False)
    def applicant_form_submit(self, **post):

        
        job_position_id = request.env['hr.job'].sudo().search([('id' , '=' , int(post.get('job_position_id') or False))])
        firstname = post.get('firstname',False)
        middlename = post.get('middlename',False)
        lastname = post.get('lastname',False)
        email_from = post.get('email_from',False)
        partner_phone = post.get('partner_phone',False)
        qualification = request.env['hr.qualification.line'].sudo().search([('id' , '=' , int(post.get('qualification') or False))])
        resume = post.get('resume',False)
        work_exp = post.get('work_exp',False)
        present_employer = post.get('present_employer',False)
        present_location = post.get('present_location',False)
        present_salary = post.get('present_salary',False)
        expected_salary = post.get('expected_salary',False)
        reference = post.get('reference',False)

        applicant_create_obj = request.env['hr.applicant'].sudo().create({
                'partner_name' : firstname,
                'middlename' : middlename,
                'lastname' : lastname,
                'email_from' : email_from,
                'partner_phone' : partner_phone,
                'applicant_qualification' : qualification.id,
                'tot_exp' : work_exp,
                'job_id' : job_position_id.id,
                'department_id' : job_position_id.department_id.id,
                'current_company' : present_employer,
                'current_location' : present_location,
                'salary_expected' : present_salary,
                'salary_proposed' : expected_salary,
                'reference' : reference
            })
        
        if post.get('Resume',False):
            name = post.get('Resume').filename
            file = post.get('Resume')
            encode_file = base64.b64encode(post.get('Resume',False).read())
            attachment_id = request.env['ir.attachment'].sudo().create({
                'name':name,
                'datas_fname': name,
                'res_name': name,
                'type': 'binary',   
                'res_model': 'hr.applicant',
                'res_id': applicant_create_obj.id,
                'datas': encode_file,
            })

        return request.render("ppts_recruitment_enhancement.thankyou_job_applied")

    @http.route("/apply-form-update", type='http', auth="public", website=True, csrf=False)
    def applicant_form_update(self, **post):

        firstname = post.get('partner_name',False)
        middlename = post.get('middlename',False)
        lastname = post.get('lastname',False)
        email_from = post.get('email_from',False)
        partner_phone = post.get('partner_phone',False)
        applicant_street = post.get('applicant_street',False)
        p_resi = post.get('p_resi',False)
        p_city = post.get('p_city',False)
        if post.get('permanent_state'):
            permanent_state = request.env['res.country.state'].sudo().search([('id' , '=' , int(post.get('permanent_state')))]).id
        else:
            permanent_state = False
        p_pin = post.get('p_pin',False)
        if post.get('p_country'):
            p_country = request.env['res.country'].sudo().search([('id' , '=' , int(post.get('p_country')))]).id
        else:
            p_country = False
        tot_exp = post.get('tot_exp',False)
        relevant_exp = post.get('relevant_exp',False)
        notice_period = post.get('notice_period',False)
        applicant_summary = post.get('applicant_summary',False)
        present_applicant_street = post.get('present_applicant_street',False)
        resi = post.get('resi',False)
        city = post.get('city',False)
        if post.get('present_state'):
            present_state = request.env['res.country.state'].sudo().search([('id' , '=' , int(post.get('present_state')))]).id
        else:
            present_state = False
        pin = post.get('pin',False)
        if post.get('present_country'):
            present_country = request.env['res.country'].sudo().search([('id' , '=' , int(post.get('present_country')))]).id
        else:
            present_country = False
        academic_info_dict = post.get('academic_info_dict',False)
        professional_info_dict = post.get('professional_info_dict',False)
        certification_info_dict = post.get('certification_info_dict',False)
        references_info_dict = post.get('references_info_dict',False)
        
        applicant_obj = request.env['hr.applicant'].sudo().search([('email_from' , '=' , email_from)])

        applicant_write_obj = applicant_obj.sudo().write({
                'partner_name' : firstname,
                'middlename' : middlename,
                'lastname' : lastname,
                'applicant_street' : applicant_street,
                'p_resi' : p_resi,
                'p_city' : p_city,
                'permanent_state' : permanent_state,
                'p_pin' : p_pin,
                'p_country' : p_country,
                'tot_exp' : tot_exp,
                'relevant_exp' : relevant_exp,
                'notice_period' : notice_period,
                'applicant_summary' : applicant_summary,
                'present_applicant_street' : present_applicant_street,
                'resi' : resi,
                'city' : city,
                'present_state' : present_state,
                'pin' : pin,
                'present_country' : present_country,
                'academic_info_dict' : academic_info_dict,
                'professional_info_dict' : professional_info_dict,
                'certification_info_dict' : certification_info_dict,
                'references_info_dict' : references_info_dict
            })

        if academic_info_dict:
            academics_list = []
            for record in eval(academic_info_dict):
                academics_list.append((0,0,{'degree':record[1] or None, 
                    'field_of_study':record[2] or None, 
                    'institute':record[3] or None, 
                    'percentage':record[4] or None, 
                    'year_of_passing':record[5] or None, 
                    }))
            for item in academics_list:
                request.env['hr.experience.academics'].sudo().create({
                    'degree':item[2]['degree'],
                    'field_of_study':item[2]['field_of_study'],
                    'institute':item[2]['institute'],
                    'percentage':item[2]['percentage'],
                    'year_of_passing':item[2]['year_of_passing'],
                    'applicant_academic_id':applicant_obj.id
                    })

        if professional_info_dict:
            professional_list = []
            for record in eval(professional_info_dict):
                start_date = end_date = ''
                if record[3]:
                    start_date = datetime.strptime(record[3], '%Y-%m-%d').strftime('%Y/%m/%d')
                if record[4]:
                    end_date = datetime.strptime(record[4], '%Y-%m-%d').strftime('%Y/%m/%d')
                professional_list.append((0,0,{'position':record[1] or None, 
                    'organization':record[2] or None, 
                    'start_date':start_date or None, 
                    'end_date':end_date or None}))
            for item in professional_list:
                request.env['hr.experience.professional'].sudo().create({
                    'position':item[2]['position'],
                    'organization':item[2]['organization'],
                    'start_date':item[2]['start_date'],
                    'end_date':item[2]['end_date'],
                    'applicant_professional_id':applicant_obj.id
                    })
                
        if certification_info_dict:
            certification_list = []
            for record in eval(certification_info_dict):
                start_date = end_date = ''
                if record[4]:
                    start_date = datetime.strptime(record[4],'%Y-%m-%d').strftime('%Y/%m/%d')
                if record[5]:
                    end_date = datetime.strptime(record[5],'%Y-%m-%d').strftime('%Y/%m/%d')
                certification_list.append((0,0,{'certifications':record[1] or None, 
                    'issued_by':record[2] or None, 
                    'state_issued':record[3] or None, 
                    'start_date':start_date or None, 
                    'end_date':end_date or None}))
            for item in certification_list:
                request.env['hr.experience.certification'].sudo().create({
                    'certifications':item[2]['certifications'],
                    'issued_by':item[2]['issued_by'],
                    'state_issued_id':item[2]['state_issued'],
                    'start_date':item[2]['start_date'],
                    'end_date':item[2]['end_date'],
                    'applicant_certification_id':applicant_obj.id,
                    })
        
        if references_info_dict:
            reference_list = []
            for record in eval(references_info_dict):
                reference_list.append((0,0,{'name':record[1] or None, 
                    'relationship':record[2] or None, 
                    'no_years':record[3] or None, 
                    'occupation':record[4] or None, 
                    'annual_income':record[5] or None, 
                    'phone_number':record[6] or None, 
                    }))
            for item in reference_list:
                request.env['applicant.reference.details'].sudo().create({
                    'name':item[2]['name'],
                    'relationship_app':item[2]['relationship'],
                    'no_years':item[2]['no_years'],
                    'occupation':item[2]['occupation'],
                    'address_details':item[2]['annual_income'],
                    'phone_no':item[2]['phone_number'],
                    'applicant_reference_id':applicant_obj.id
                    })

        return request.render("ppts_experience.thankyou_applicant_form_update")


class WebsiteSurvey(WebsiteSurvey):
    # HELPER METHODS #

    # Printing routes
    @http.route(['/survey/print/<model("survey.survey"):survey>',
                 '/survey/print/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)
    def print_survey(self, survey,token=None, **post):
        '''Display an survey in printable view; if <token> is set, it will
        grab the answers of the user_input_id that has <token>.'''
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        action_obj = env['ir.actions.actions']
        action_ids = action_obj.sudo().search([('name','=','Applications')]).ids
        action_id = action_obj.sudo().browse(action_ids[1])
        menu_obj = env['ir.ui.menu']
        menu_obj_ids = menu_obj.sudo().search([('name','=','Recruitment')]).ids
        menu_id = menu_obj.sudo().browse(menu_obj_ids[0])
        
        return request.render('survey.survey_print',
                                      {'survey': survey,
                                       'token': token,
                                       'page_nr': 0,
                                       'applicant_id': survey.applicant_id.id,
                                       'action_id': action_id.id,
                                       'menu_id': menu_id.id,
                                       'quizz_correction': True if survey.quizz_mode and token else False})


    # Survey start
    @http.route(['/survey/start/<model("survey.survey"):survey>',
                 '/survey/start/<model("survey.survey"):survey>/<string:token>'],
                type='http', auth='public', website=True)

    def start_survey(self, survey, token=None, **post):
        UserInput = request.env['survey.user_input']
        print('lllllllllllllllllllll',survey.id)
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))
        action_obj = env['ir.actions.actions']
        action_ids = action_obj.sudo().search([('name','=','Applications')]).ids
        action_id = action_obj.sudo().browse(action_ids[1])
        menu_obj = env['ir.ui.menu']
        menu_obj_ids = menu_obj.sudo().search([('name','=','Recruitment')]).ids
        menu_id = menu_obj.sudo().browse(menu_obj_ids[0])

        # Test mode
        if token and token == "phantom":
            _logger.info("[survey] Phantom mode")
            user_input = UserInput.create({'survey_id': survey.id, 'test_entry': True})
            data = {'survey': survey, 'page': None, 'token': user_input.token}
            return request.render('survey.survey_init', data)
        # END Test mode

        # Controls if the survey can be displayed
        errpage = self._check_bad_cases(survey, token=token)
        if errpage:
            return errpage

        # Manual surveying
        if not token:
            vals = {'survey_id': survey.id}
            if request.website.user_id != request.env.user:
                vals['partner_id'] = request.env.user.partner_id.id
            user_input = UserInput.create(vals)
        else:
            user_input = UserInput.sudo().search([('token', '=', token)], limit=1)
            if not user_input:
                return request.render("website.403")

        # Do not open expired survey
        errpage = self._check_deadline(user_input)
        if errpage:
            return errpage
        # Select the right page
        if user_input.state == 'new':  # Intro page
            
            data = {'survey': survey, 'page': None, 'token': user_input.token,'applicant_id': survey.applicant_id.id,
                                       'action_id': action_id.id,
                                       'menu_id': menu_id.id}
            
            return request.render('survey.survey_init', data)
        else:
           
            return request.redirect('/survey/fill/%s/%s' % (survey.id, user_input.token))
            