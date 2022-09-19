from odoo import api, models
from datetime import datetime


class DwrWeeklyReport(models.AbstractModel):
    
    _name = 'report.custom_crm.report_dwrcrm_week'
    
    @api.model
    def get_report_values(self, docids, data=None):
        lead = {};states = []
        tele = [];odoo = [];pre_sale = [];other = [];web = [];total = [];row = [];partner = ""
        dwr_setback = [];training_activity = [];review_activity = [];key_observation = [];other_details = [];date_list = []
        odoo_demo = 0;telesales_demo = 0;presales_demo = 0;any_other_sources_demo = 0;no_show_demo = 0
        for doc in docids:
            dwr_id = self.env['crm.dwr'].search([('id', '=', doc)])
            crm_id = self.env['crm.lead'].search([])
            for rec in crm_id:
                if rec.create_date:
                    date = str(datetime.strptime(rec.create_date, '%Y-%m-%d %H:%M:%S').date())
                    if date == dwr_id.name:
                        if rec.source_id.name == 'Telesales':
                            tele.append(rec)
                            total.append(rec)
                        if rec.source_id.name == 'Presales':
                            pre_sale.append(rec)
                            total.append(rec)
                        if rec.source_id.name == 'Referals':
                            other.append(rec)
                            total.append(rec)
                        if rec.source_id.name == 'Website':
                            web.append(rec)
                            total.append(rec)
                        if rec.source_id.name == 'Odoo USA' or rec.source_id.name == 'Odoo India' or rec.source_id.name == 'Odoo France' or rec.source_id.name == 'Odoo EU' :
                            odoo.append(rec)
                            total.append(rec)
            if dwr_id.name:
                date_list.append(str(dwr_id.name))
            if dwr_id.dwr_setback:
                dwr_setback.append(dwr_id.dwr_setback)
            if dwr_id.training_activity:
                training_activity.append(dwr_id.training_activity)
            if dwr_id.review_activity:
                review_activity.append(dwr_id.review_activity)  
            if dwr_id.key_observation:
                key_observation.append(dwr_id.key_observation)
            if dwr_id.other_details:
                other_details.append(dwr_id.other_details) 
            if dwr_id.odoo_demo:
                odoo_demo += dwr_id.odoo_demo
            if dwr_id.telesales_demo:
                telesales_demo += dwr_id.telesales_demo
            if dwr_id.presales_demo:
                presales_demo += dwr_id.presales_demo
            if dwr_id.any_other_sources_demo:
                any_other_sources_demo += dwr_id.any_other_sources_demo
            if dwr_id.no_show_demo:
                no_show_demo += dwr_id.no_show_demo
            if dwr_id.client_state_ids:
                for state in dwr_id.client_state_ids:
                    line = {}
                    line['client_name_id'] = state.client_name_id.name
                    line['area'] = state.area
                    line['value'] = state.value
                    line['details'] = state.details
                    states.append(line)
        date_list.sort()
        last = len(date_list)
        lead['date_max'] = date_list[last-1] 
        lead['date_min'] = date_list[0] 
        lead['dwr_setback'] = dwr_setback
        lead['training_activity'] = training_activity
        lead['review_activity'] = review_activity
        lead['key_observation'] = key_observation
        lead['other_details'] = other_details
        lead['odoo_lead'] = len(odoo)
        lead['telesales_lead'] = len(tele)
        lead['presales_lead'] = len(pre_sale)
        lead['any_other_sources_lead'] = len(other)
        lead['website_lead'] = len(web)
        lead['odoo_demo'] = odoo_demo
        lead['telesales_demo'] = telesales_demo
        lead['presales_demo'] = presales_demo
        lead['any_other_sources_demo'] = any_other_sources_demo
        lead['no_show_demo'] = no_show_demo
        lead['client_state_ids'] = states
        
        if total:
            count = len(total)
            for res in total:
                if res.partner_id:
                    row.append(res.partner_id)
            if row:
                row_set = set(row)
                for rec in row_set:
                    if partner == "":
                        partner = str(rec.name)
                    else:
                        partner = str(rec.name) + "," + partner
                lead['dwr_success'] = str(count) + ' - (' + partner + ')'
            else:
                lead['dwr_success'] = str(count)      
        else:
            lead['dwr_success'] = ''
        
        return {
            'doc': lead,
        }
    
