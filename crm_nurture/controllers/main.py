# -*- coding: utf-8 -*-
from odoo import SUPERUSER_ID
from odoo import http
from odoo.http import Controller, route, request
import urllib.parse

class crm_nurture_unsubscribe(http.Controller):

    @http.route(['/Unsubscribe'], type='http', auth="public", website=True)
    def Unsubscribe(self, **kwargs):

        url = http.request.httprequest.full_path
        par = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
        model_name = str(par['model'][0])
        obj_id = int(par['obj_id'][0])
        if model_name == 'res.partner':
            partner_id = request.env[model_name].sudo().search([('id', '=', obj_id)])
            partner_id.opt_out = True
            partner_id.followup_line_ids.unlink()

        if model_name == 'crm.lead':
            lead_id = request.env[model_name].sudo().search([('id', '=', obj_id)])
            lead_id.opt_out = True
            lead_id.lead_followup_line_ids.unlink()

        values = {
            'error': {},
        }
        return request.render("crm_nurture.unsubscribe",values)

class website_crm_nurture(http.Controller):

    @http.route(['/lead_form'], type='http', auth="public", website=True)
    def form_builder(self, **kwargs):
        campaign_ids = request.env['crm.campaign'].sudo().search([])
        state_ids = request.env['res.country.state'].sudo().search([])
        country_ids = request.env['res.country'].sudo().search([])

        values = {
            'states':state_ids,
            'countries':country_ids,
            'campaigns':campaign_ids,
            'error': {},
        }
        return request.render("crm_nurture.create_lead",values)

    @http.route('/Lead/detailed_save/', methods=['POST'], type='http', auth="public", website=True,csrf=False)
    def Lead_save(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        env = request.env(user=SUPERUSER_ID)
        value = {}
        values = {}
        user_id=uid
        subject=post.pop('lead_subject', False)
        company_name = post.pop('company_name', False)
        street2 = post.pop('street2', False)
        first_name=post.pop('prospect_first_name', False)
        last_name=post.pop('prospect_last_name', False)
        mail_id = post.pop('prospect_mail_id', False)
        phone = post.pop('prospect_phone', False)
        street = post.pop('street', False)
        city = post.pop('city', False)
        state_id = post.pop('state_id', False)
        country_id = post.pop('country_id', False)

        imd = request.env['ir.model.data']
        follow_ups =[]
        campaign_id = imd.xmlid_to_res_id('crm_nurture.crm_campaign_2')
        if campaign_id and request.env['crm.campaign'].sudo().browse(campaign_id).email_template_ids:
            follow_ups.append((0, 0, {'crm_campaign_id': campaign_id}))
        value['user_id']=user_id
        if not first_name:
            first_name =""
        if not last_name:
            last_name =""
        
        
        values = {
            'name':subject,
            'contact_name' :str(first_name) + " " +str(last_name),
            'partner_name':company_name,
            'street':street,
            'street2':street2,
            'city':city,
            'state_id':state_id,
            'country_id':country_id,
            'phone':phone,
            'email_from':mail_id,
            'lead_followup_line_ids':follow_ups
        }

        env['crm.lead'].sudo().create(values)
        return request.render("crm_nurture.confirmation", values)

class website_crm_nurture_2(http.Controller):
    @http.route(['/lead_form_2'], type='http', auth="public", website=True)
    def form_builder(self, **kwargs):
        values = {
            'error': {},
        }
        return request.render("crm_nurture.create_lead_2",values)

    @http.route('/Lead/simplified_save/', methods=['POST'], type='http', auth="public", website=True, csrf=False)
    def Lead_save(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry
        env = request.env(user=SUPERUSER_ID)
        value = {}
        values = {}
        user_id = uid
        subject = post.pop('lead_subject', False)
        mail_id = post.pop('prospect_mail_id', False)

        imd = request.env['ir.model.data']
        follow_ups = []
        campaign_id = imd.xmlid_to_res_id('crm_nurture.crm_campaign_1')
        if campaign_id and request.env['crm.campaign'].sudo().browse(campaign_id).email_template_ids:
            follow_ups.append((0, 0, {'crm_campaign_id': campaign_id}))
        value['user_id'] = user_id
        
        values = {
            'name': subject,
            'email_from': mail_id,
            'lead_followup_line_ids': follow_ups
        }

        env['crm.lead'].sudo().create(values)
        return request.render("crm_nurture.confirmation", values)