from odoo import fields, models, api
from datetime import datetime, date, timedelta 


class CustomCrm(models.Model):
    _inherit = "crm.lead"
    
    def _get_date_field(self):
        for rec in self:
            if rec.id:
                crm_id = self.env['crm.lead'].search([('id', '=', rec.id)])
                if crm_id:
                    rec.active_date = crm_id.write_date
                    rec.create_date = crm_id.date_open
                
    def _get_date_cal(self):
        for rec in self:
            if rec.create_date and rec.write_date:
                fmt = '%Y-%m-%d %H:%M:%S'
                create_date = datetime.strptime(rec.create_date, fmt)
                last_active = datetime.strptime(rec.write_date, fmt)
                time_now = datetime.now()
                age = str(time_now - create_date).split(':')
                time = str(time_now - last_active).split(':')
                if len(time) == 4:
                    rec.no_active_date = time[1] + ' ago'
                elif len(time) == 3:
                    if time[0] == '0':
                        rec.no_active_date = time[1] + ' minutes ago' 
                    else:
                        rec.no_active_date = time[0] + ' hours ago' 
                if len(age) == 4:
                    rec.age_of_date = age[1]
                elif len(age) == 3:
                    if age[0] == '0':
                        rec.age_of_date = age[1] + ' minutes' 
                    else:
                        rec.age_of_date = age[0] + ' hours' 
                rec.date_diff = str((time_now - last_active).days + 1)
                
    create_date = fields.Datetime(string='Create Date', compute='_get_date_field', copy=False)
    active_date = fields.Datetime(string='Last Activity Date', compute='_get_date_field', copy=False)
    no_active_date = fields.Char(string='No Activity Since', compute='_get_date_cal', copy=False)
    date_diff = fields.Char(string='Date Different', compute='_get_date_cal', copy=False, default='0')
    next_activity_ids = fields.One2many('mail.activity', 'crm_lead_id', string='Next Activity Date', readonly=True)
    industry_id = fields.Many2one('crm.industry', string='Industry', required=True, track_visibility='always')
    services_id = fields.Many2one('crm.services', string='Services', required=True, track_visibility='always')
    last_action = fields.Boolean('last Activity', compute='get_last_date', default=False)
    to_mail_send = fields.Boolean('Send mail')
    email_list = fields.Char('Email List', compute='_get_to_email_list')
    age_of_date = fields.Char(string='Age of the Opportunity', compute='_get_date_cal', copy=False, default='0')
    lead_product_ids = fields.One2many('crm.lead.product', 'lead_id', string='Products For Quotation')

    @api.model
    def create(self, vals):
        res = super(CustomCrm, self).create(vals)
        assign_follow_id = self.env['assign.followers.settings'].search([('is_check', '=', True)])
        for assign in assign_follow_id:
            if assign:
                assign.create_action(res.id)
        return res
        
    @api.depends('date_open')
    def _compute_day_open(self):
        """ Compute difference between create date and open date """
        for lead in self.filtered(lambda l: l.date_open):
            if lead.create_date and lead.date_open:
                date_create = fields.Datetime.from_string(lead.create_date)
                date_open = fields.Datetime.from_string(lead.date_open)
                lead.day_open = abs((date_open - date_create).days)
                
    @api.depends('date_closed')
    def _compute_day_close(self):
        """ Compute difference between current date and log date """
        for lead in self.filtered(lambda l: l.date_closed):
            if lead.create_date and lead.date_closed:
                date_create = fields.Datetime.from_string(lead.create_date)
                date_close = fields.Datetime.from_string(lead.date_closed)
                lead.day_close = abs((date_close - date_create).days)
            
    @api.depends('email_list')
    def _get_to_email_list(self):
        for order in self:
            row = ""
            if self.user_id:
                if row == "":
                    row = str(self.user_id.partner_id.id)
            mail_follow_id = self.env['mail.followers'].search([('res_model', '=', 'crm.lead'), ('res_id', '=', order.id)])    
            if mail_follow_id:
                for rec in mail_follow_id:
                    if rec.partner_id:
                        if row == "":
                            row = str(rec.partner_id.id)
                        else:
                            row = str(rec.partner_id.id) + "," + row
                    if rec.channel_id:
                        mail_channel_id = self.env['mail.channel'].search([('id', '=', rec.channel_id.id)])
                        if mail_channel_id.channel_last_seen_partner_ids:
                            for channel in mail_channel_id.channel_last_seen_partner_ids:
                                if row == "":
                                    row = str(channel.partner_id.id)
                                else:
                                    row = str(channel.partner_id.id) + "," + row
                order.email_list = row
                
    @api.multi
    def get_last_date(self):
        if self:
            for rec in self:
                if rec.next_activity_ids:
                    for line in rec.next_activity_ids:
                        fmt = '%Y-%m-%d'
                        last_active = datetime.strptime(line.date_deadline, fmt)
                        date = datetime.today() - timedelta(1)
                        if date > last_active:
                            line.write({'last_action': True})
                rec.last_action = True
 
    def crm_next_activity_mail(self):
        crm_id = self.env['crm.lead'].search([])
        for rec in crm_id:
            if not rec.stage_id.name in ('Won / Existing Clients / Completed','Lost'):
                if rec.date_diff:
                    diff = int(rec.date_diff)
                    if diff > 5 and not rec.next_activity_ids:
                        template_id = self.env.ref('custom_crm.crm_activity_mail_template')
                        if template_id:
                            template_id.send_mail(rec.id, force_send=True)
                    if diff > 5 and rec.next_activity_ids:
                        for next in rec.next_activity_ids:
                            if next.date_diff:
                                count = int(next.date_diff)
                                if count > 5:
                                    template_id = self.env.ref('custom_crm.crm_activity_mail_template')
                                    if template_id:
                                        template_id.send_mail(rec.id, force_send=True)
    
