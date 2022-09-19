from odoo import api, fields, models, tools, _
from datetime import datetime, timedelta
from datetime import date
import dateutil.relativedelta
import calendar
import dateutil.parser

MONTH_LIST = [('1', 'Jan'), ('2', 'Feb'), ('3', 'Mar'), ('4', 'Apr'), ('5', 'May'), ('6', 'Jun'), ('7', 'Jul'), ('8', 'Aug'), ('9', 'Sep'), ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')]


class CRMDashboard(models.Model):
    _name = 'crm.dashboard'
    
    def daterange(self, a_start, b_end):
        for n in range(int ((b_end - a_start).days)):
            yield a_start + timedelta(n)

    @api.model
    def fetch_dashboard_data(self, team=False, person=False, week=False, quarter=False, month=False,year_click=False):
        result = {}
        state_list = []
        stae_revenue = []
        dates_count = []
        stae_revenue_sum = []
        mem_list = []
        state_leads = []
        sale_team_list = []
        sales_member_list = []
        state_leads.append(0)
        crm_state = self.env['crm.stage'].search([])
        if team == '--Select Sales Team--':
            team = False
        if person == '--Select Sales Person--':
            person = False
        if team and person:
            teams_data = self.env['crm.team'].browse(int(team))
            person_data = self.env['res.users'].browse(int(person))
        if team and not person:
            teams_data = self.env['crm.team'].browse(int(team))
            person_data = self.env['res.users'].search([('id', '=', self.env.user.id)])
        if not team and person:
            teams_data = self.env['crm.team'].search([('member_ids', 'in', self.env.user.id)])
            person_data = self.env['res.users'].browse(int(person))    
        if not team and not person:
            teams_data = self.env['crm.team'].search([])
            person_data = self.env['res.users'].search([])
        emp_mem_list = []
        emp_mem_ids = []
        deta = []
        emp_mem_list.append(self.env.user.name)
        for stages in crm_state:
            sum_reve = 0
            sum_reve_no_dec = 0
            sum_reve_tot = 0
            month_list = []
            details = []
            month_list.append(stages.name)
            d = date.today() - dateutil.relativedelta.relativedelta(months=1)
            dates_count = []
            week_list=[]  
            if week == "1":
                week_list.append(week) 
                
            for month in range(1, 7):
                if week == None and quarter == None and year_click == None:
                    d2 = d + dateutil.relativedelta.relativedelta(months=1)
                    d = d2
                    s = d.strftime('%m')
                    y = d.strftime('%Y')
                    month_name = calendar.month_name[int(s)]
                    dates_count.append(month_name + '-' + str(y))   
                    rev = 0
                    crm_mem_leads = self.env['crm.lead'].search([('team_id', 'in', teams_data.ids), ('user_id', 'in', person_data.ids), ('stage_id', '=', stages.id)])                        
                    for resul in crm_mem_leads:
                        if resul.date_deadline:
                            month_count = datetime.strptime(resul.date_deadline, '%Y-%m-%d').strftime('%m')
                            if int(month_count) == int(s):
                                rev += resul.planned_revenue
                                rev = int(rev)
                    month_list.append('₹'+str("{:,}".format(rev)))
                
            if week == "1":
                
                week2 = date.today() - dateutil.relativedelta.relativedelta(days=7)
                dates_count = []
                rev = 0
                for weeks in range(1, 7):
                    rev = 0
                    week2 = week2 + dateutil.relativedelta.relativedelta(days=7)
                    fiscal_period_id = self.env['periods.week'].search([
                    ('year', '=', week2.strftime('%Y')),
                    ('start_date', '<=', week2),
                    ('end_date', '>=', week2)])
                    if fiscal_period_id:
                        s = week2.strftime('%m')
                        y = week2.strftime('%Y')
                        month_name = calendar.month_name[int(s)]
                        dates_count.append([str(month_name) + '-' + str(y) , fiscal_period_id.week_name])
                        crm_mem_leads = self.env['crm.lead'].search([('team_id', '=', teams_data.ids), ('user_id', '=', person_data.ids), ('stage_id', '=', stages.id)])                        
                        
                        for resul in crm_mem_leads:
                            if resul.date_deadline:
                                month_count = datetime.strptime(resul.date_deadline, '%Y-%m-%d')
                                if str(month_count) >= str(fiscal_period_id.start_date) and str(month_count) <= str(fiscal_period_id.end_date):
                                    rev += resul.planned_revenue
                                    rev = int(rev)
                        month_list.append('₹'+str("{:,}".format(rev)))
                    
            if quarter == "1":
                week2 = date.today() - dateutil.relativedelta.relativedelta(months=3)
                dates_count = []
                rev = 0
                for weeks in range(1, 7):
                    rev = 0
                    week2 = week2 + dateutil.relativedelta.relativedelta(months=3)
                    start_date_quarter = week2 
                    end_date_quarter = start_date_quarter - dateutil.relativedelta.relativedelta(months=3)
                    print(week2, week2.strftime('%Y'))
                    fiscal_period_id = self.env['periods.generate'].search([
                    ('year', '=', week2.strftime('%Y')),
                    ('start_date', '<=', week2),
                    ('end_date', '>=', week2)])
                    print(fiscal_period_id)
                    if fiscal_period_id:
                        s = week2.strftime('%m')
                        y = week2.strftime('%Y')
                        dates_count.append('Q' + str(fiscal_period_id.quarter) + '-' + str(y))
                        crm_mem_leads = self.env['crm.lead'].search([('team_id', '=', teams_data.ids), ('user_id', '=', person_data.ids), ('stage_id', '=', stages.id)])                        
                        for resul in crm_mem_leads:
                            if resul.date_deadline:
                                month_count = datetime.strptime(resul.date_deadline, '%Y-%m-%d')
                               
                                if dateutil.parser.parse(str(month_count)).date() <= start_date_quarter and dateutil.parser.parse(str(month_count)).date() >= end_date_quarter:
                                    rev += resul.planned_revenue
                                    rev = int(rev)
                        month_list.append('₹'+str("{:,}".format(rev)))    
                        
                        
            if year_click == "1":
                week2 = date.today() - dateutil.relativedelta.relativedelta(years=1)
                dates_count = []
                rev = 0
                for weeks in range(1, 3):
                    rev = 0
                    week2 = week2 + dateutil.relativedelta.relativedelta(years=1)
                    rec_year = week2.strftime('%Y')
                    a = date(int(rec_year), 1, 1)
                    b = date(int(rec_year), 12, 31)
                    dates_count.append('Y' +'-'+ rec_year)
                    crm_mem_leads = self.env['crm.lead'].search([('team_id', '=', teams_data.ids), ('user_id', '=', person_data.ids), ('stage_id', '=', stages.id)])                        
                    for resul in crm_mem_leads:
                        if resul.date_deadline:
                            month_count = datetime.strptime(resul.date_deadline, '%Y-%m-%d')
                            if dateutil.parser.parse(str(month_count)).date() >= a and dateutil.parser.parse(str(month_count)).date() <= b:
                                rev += resul.planned_revenue
                                rev = int(rev)
                    month_list.append('₹'+str("{:,}".format(rev)))                   
#               
            details.append(month_list)
            crm_mem_leads = self.env['crm.lead'].search([('team_id', '=', teams_data.ids), ('user_id', '=', person_data.ids), ('stage_id', '=', stages.id)])                        
            for resul in crm_mem_leads:
                sum_reve += resul.planned_revenue
                sum_reve_no_dec = int(sum_reve)
                sum_reve_tot = sum_reve_no_dec / len(crm_mem_leads)
                        
            deta.append(details)
            sum_reve_tot = "%.2f" %(sum_reve_tot)

            stae_revenue.append( ('₹'+str("{:,}".format(sum_reve_no_dec))))
            value_sep = "{:,}".format(float(sum_reve_tot))
            stae_revenue_sum.append('₹'+str(value_sep))
            
            state_leads.append(len(crm_mem_leads))
            emp_mem_list.append(len(crm_mem_leads))
            state_list.append(stages.name)
#             if week == "1":
#                 state_leads.append(len(crm_mem_leads))
#                 emp_mem_list.append(len(crm_mem_leads))
#                 state_list.append(stages.name)
    
        emp_mem_ids.append(self.env.user.id)
        mem_list.append(emp_mem_list)
        
        result['week_list'] = week 
        print(result['week_list'],"result['week_list']")
        result['deta'] = deta 
        print(result['deta'])  
        result['dates_count'] = dates_count
        result['state'] = state_list
        result['state_revenue'] = stae_revenue
        result['state_revenue_sum'] = stae_revenue_sum
        result['lead_states_rec'] = state_leads
        result['emp_name'] = mem_list
        result['emp_list_mem_ids'] = emp_mem_ids
        
        sales_te = self.env['crm.team'].search([])
        for teams in sales_te:
            if teams.member_ids:
                sale_teams = {}
                sale_teams['id'] = teams.id
                sale_teams['name'] = teams.name
                sale_team_list.append(sale_teams)
        result['sale_team'] = sale_team_list
        if not team or team == "--Select Sales Team--":
            sales_mem = self.env['res.users'].search([])
            for member in sales_mem:
                sales_members = {}
                sales_members['id'] = member.id
                sales_members['name'] = member.name
                sales_member_list.append(sales_members)
            result['sales_member'] = sales_member_list
        else:
            team_id = int(team[0])
            sales_mem = self.env['res.users'].search([('sale_team_id', '=', team_id)])
            for member in sales_mem:
                sales_members = {}
                sales_members['id'] = member.id
                sales_members['name'] = member.name
                sales_member_list.append(sales_members)
            result['sales_member'] = sales_member_list
        return result
