
from odoo import http, _
from odoo.addons.http_routing.models.ir_http import slug
from odoo.http import request
from odoo.addons.website_hr_recruitment.controllers.main import WebsiteHrRecruitment

class WebsiteHrRecruitment(WebsiteHrRecruitment):
    def sitemap_jobs(env, rule, qs):
        if not qs or qs.lower() in '/jobs':
            yield {'loc': '/jobs'}

    @http.route([
        '/jobs',
        '/jobs/country/<model("res.country"):country>',
        '/jobs/department/<model("hr.department"):department>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>',
        '/jobs/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/office/<int:office_id>',
        '/jobs/department/<model("hr.department"):department>/office/<int:office_id>',
        '/jobs/country/<model("res.country"):country>/department/<model("hr.department"):department>/office/<int:office_id>',
    ], type='http', auth="public", website=True, sitemap=sitemap_jobs)
    def jobs(self, country=None, department=None, office_id=None, **kwargs):
        env = request.env(context=dict(request.env.context, show_address=True, no_tag_br=True))

        Country = env['res.country']
        Jobs = env['hr.job']

        # List jobs available to current UID
        job_ids = Jobs.search([], order="website_published desc,no_of_recruitment desc").ids
        # Browse jobs as superuser, because address is restricted
        jobs = Jobs.sudo().browse(job_ids)

        # Default search by user country
        if not (country or department or office_id or kwargs.get('all_countries')):
            country_code = request.session['geoip'].get('country_code')
            if country_code:
                countries_ = Country.search([('code', '=', country_code)])
                country = countries_[0] if countries_ else None
                if not any(j for j in jobs if j.address_id and j.address_id.country_id == country):
                    country = False

        # Filter job / office for country
        if country and not kwargs.get('all_countries'):
            jobs = [j for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id]
            offices = set(j.address_id for j in jobs if j.address_id is None or j.address_id.country_id and j.address_id.country_id.id == country.id)
        else:
            offices = set(j.address_id for j in jobs if j.address_id)

        # Deduce departments and countries offices of those jobs
        departments = set(j.department_id for j in jobs if j.department_id)
        countries = set(o.country_id for o in offices if o.country_id)

        if department:
            jobs = [j for j in jobs if j.department_id and j.department_id.id == department.id]
        if office_id and office_id in [x.id for x in offices]:
            jobs = [j for j in jobs if j.address_id and j.address_id.id == office_id]
        else:
            office_id = False
        val = []
        att = {}
        print(departments)
        for dep in departments:
            list = [dep]
#             parent = []
            for lis in list:
                if lis.parent_id:
                    list.append(lis.parent_id)
                else:
#                     list.remove(lis)
                    val.append({lis:list})
        print(val)
        for re in val:
            for key,value in re.items():
                if value:
                    att.setdefault(key,[]).append(value[0].id)
        print(att)

        jobs = request.env['hr.job'].sudo().search([('state', '=' , 'recruit')])
        print(jobs,'ee')
        return request.render("ppts_experience.index_ppts_experience", {
            'jobs': jobs,
        })
                    
        # Render page
        # return request.render("website_hr_recruitment.index", {
        #     'jobs': jobs,
        #     'countries': countries,
        #     'departments': departments,
        #     'offices': offices,
        #     'country_id': country,
        #     'department_id': department,
        #     'office_id': office_id,
        #     'parent_departments':att,
        # })

class WebsiteMprfRequest(http.Controller):
    @http.route("/mprfrequest", type='http', auth="public", website=True, csrf=False)
    def mprf_form(self, **kwargs):
        
        jobs = request.env['hr.job'].sudo().search([])
        dept = request.env['hr.department'].sudo().search([])
        manpower_reason = request.env['reason.manpower'].sudo().search([])
        qualification = request.env['hr.qualification.line'].sudo().search([])
        skills = request.env['hr.keyskills.line'].sudo().search([])
        reporting_to = request.env['hr.employee'].sudo().search([])
        requested_by = request.env['hr.employee'].sudo().search([])
        emp_type = request.env['hr.contract.type'].sudo().search([])
        job_sen_title = request.env['hr.job.seniority.title'].sudo().search([])

        
        return request.render("ppts_experience.mprf_request",{
            'jobs' : jobs,
            'dept' : dept,
            'manpower_reason' : manpower_reason,
            'qualification' : qualification,
            'skills' : skills,
            'reporting_to' : reporting_to,
            'requested_by' : requested_by,
            'emp_type' : emp_type,
            'job_sen_title' : job_sen_title
            })


    @http.route("/mprfsubmit", type='http', auth="public", website=True, csrf=False)
    def mprf_form_submit(self, **post):

        department_id = request.env['hr.department'].sudo().search([('id' , '=' , int(post.get('department_id')))])  
        num_of_positions = post.get('num_of_positions',False)  
        from_exp = post.get('from_exp',False)  
        to_exp = post.get('to_exp',False)  
        manpower_reason = request.env['reason.manpower'].sudo().search([('id' , '=' , int(post.get('manpower_reason')))])
        qualification_required = request.env['hr.qualification.line'].sudo().search([('id' , '=' , int(post.get('qualification_required')))])
        reporting_to = request.env['hr.employee'].sudo().search([('id' , '=' , int(post.get('reporting_to') or False))])  
        job_position_id = request.env['hr.job'].sudo().search([('id' , '=' , int(post.get('job_position_id')))])   
        tentative_doj = post.get('tentative_doj',False)  
        gender = post.get('gender',False)  
        skills_required = request.env['hr.keyskills.line'].sudo().search([('id' , '=' , int(post.get('skills_required')))])  
        other_skills = post.get('other_skills',False)  
        budget_from = post.get('budget_from',False)  
        budget_to = post.get('budget_to',False)  
        employement_type = request.env['hr.contract.type'].sudo().search([('id' , '=' , int(post.get('employement_type')))])  
        period_count = post.get('period_count',False)  
        period_type = post.get('period_type',False)  
        requested_by = request.env['hr.employee'].sudo().search([('id' , '=' , int(post.get('requested_by')))])   
        designation = post.get('designation',False)  
        requested_date = post.get('requested_date',False)  
        job_description = post.get('job_description',False)  

        print('-----------',period_type,'-----------')     

        mprf_create_obj = request.env['mprf.request'].sudo().create({
                'department_id' : department_id.id,
                'num_of_positions' : num_of_positions,
                'from_exp' : from_exp,
                'to_exp' : to_exp,
                'manpower_reason' : manpower_reason.id,
                'qualification_required' : [(6, 0,[qualification_required.id])],
                'reporting_to' : reporting_to.id,
                'job_position_id' : job_position_id.id,
                'tentative_doj' : tentative_doj,
                'gender' : gender,
                'skills_required' : [(6, 0,[skills_required.id])],
                'other_skills' : other_skills,
                'budget_from' : budget_from,
                'budget_to' : budget_to,
                'employement_type' : employement_type.id,
                'period_count' : period_count,
                'period_type' : period_type,
                'requested_by' : requested_by.id,
                'designation' : designation,
                'requested_date' : requested_date,
                'job_description' : str(job_description),
                'status' : 'requested',
                'mprf_job_position_id' : job_position_id.id,
            })

        return request.render("ppts_experience.thankyou_mprf_request")