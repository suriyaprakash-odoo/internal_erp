from odoo import api, fields, models, _
from datetime import datetime, timedelta
import pytz
from odoo import SUPERUSER_ID
from odoo.exceptions import UserError
import time
from odoo import exceptions, _
from pytz import timezone
from dateutil.tz import tzlocal

# from passlib.tests.utils import limit


# class for converting the datatime to UTC
class time_convert(models.Model):
    _name = "time.conversion"

    @api.multi
    def time_conversion(self, delay_days, time_to_send, tz):
        delay_days_no = delay_days
        send_time = time_to_send
        tzone = tz

        utc_now_dt = datetime.utcnow() + timedelta(days=delay_days_no)  # utcnow class method
        utc_now_dt_convert = utc_now_dt.replace(tzinfo=pytz.UTC)  # replace method
        local_tz = pytz.timezone(tzone)
        utc_localize = utc_now_dt_convert.astimezone(local_tz)  # astimezone method
        tm_obj = datetime.strptime(send_time, '%H:%M')
        date_time_combine = datetime.combine(utc_localize, datetime.time(tm_obj))
        dt_string = date_time_combine.strftime("%Y-%m-%d %H:%M:%S")
        date_obj = datetime.strptime(dt_string, "%Y-%m-%d %H:%M:%S")
        local_tm = local_tz.localize(date_obj, is_dst=None)
        final_utc_dt = local_tm.astimezone(pytz.utc)

        return final_utc_dt


class EmailFollowupLine(models.Model):
    _name = "email.followup.line"

    crm_campaign_id = fields.Many2one("crm.campaign", string="Campaign Tag")
    next_mail_date = fields.Datetime("Next Mail Time")
    next_template_id = fields.Many2one("mail.template", "Next Mail")
    added_date = fields.Datetime(" Tag Added Time")
    mail_seq = fields.Integer("Mail Sequence")

    @api.model
    def create(self, vals):
        tz = ''
        if vals.get('partner_id'):
            ref_id = self.env["res.partner"].search([("id", '=', vals.get('partner_id'))])
            tz = ref_id.tz
        if vals.get('lead_id'):
            ref_id = self.env["crm.lead"].search([("id", '=', vals.get('lead_id'))])
            tz = ref_id.partner_id.tz
        if not tz:
            user_pool = self.env['res.users'].browse(SUPERUSER_ID)
            if user_pool.tz == False:
                raise UserError(_('Timezone is not given for the user'))
            tz = str(pytz.timezone(user_pool.partner_id.tz) or pytz.utc)

        template_ids = self.env["crm.campaign"].search([("id", '=', vals.get('crm_campaign_id'))])
        if not template_ids.email_template_ids:
            raise UserError(('Please select a Campaign with Email Templates. Contact Administrator for more Information.'))
        mail_template = template_ids.email_template_ids.filtered(lambda line: line.mail_sequence == 1)
        if mail_template and mail_template.send_now:
            mail_template.template_id.send_mail(ref_id.id, force_send=True, raise_exception=True)
            next_templates = template_ids.email_template_ids.filtered(lambda line: line.mail_sequence > 1)
            if next_templates:
                mail_template = next_templates[0]
                
        final_utc_date = self.env["time.conversion"].time_conversion(mail_template.delay_days, mail_template.time_to_send, tz)
        vals['next_template_id'] = mail_template.template_id.id
        vals['next_mail_date'] = final_utc_date
        vals['added_date'] = datetime.utcnow()
        vals['mail_seq'] = mail_template.mail_sequence

        follow_up = super(EmailFollowupLine, self).create(vals)

        return follow_up

    @api.onchange('crm_campaign_id')
    def onchange_crm_campaign(self):
        if self.crm_campaign_id:
            self.added_date = datetime.now()
            if self.partner_id:
                tz = self.partner_id.tz
            if self.lead_id:
                tz = self.lead_id.partner_id.tz
            if not tz:
                user_pool = self.env['res.users'].browse(SUPERUSER_ID)
                tz = str(pytz.timezone(user_pool.partner_id.tz) or pytz.utc)

            for line in self.crm_campaign_id.email_template_ids:
                if line.mail_sequence == 1:
                    final_utc_date = self.env["time.conversion"].time_conversion(line.delay_days, line.time_to_send, tz)

                    self.mail_seq = line.mail_sequence
                    self.next_template_id = line.template_id.id
                    self.next_mail_date = final_utc_date


class MailTrackingEmail(models.Model):
    _inherit = "mail.tracking.email"

    @api.multi
    @api.depends('mail_message_id')
    def _get_message_id(self):
        for mail in self:
            if mail.mail_message_id:
                if mail.mail_message_id.model == "crm.lead":
                    mail.lead_id = mail.mail_message_id.res_id

    lead_id = fields.Many2one("crm.lead", compute="_get_message_id", string="CRM Lead ID", store=True)


class campaign_mail_templates(models.Model):
    _name = "campaign.mail.template"
    _order = "mail_sequence"
    
    # default get method for generating the sequence for next line item
    @api.model
    def default_get(self, fields):
        res = {}
        if self.env.context:
            context_keys = self.env.context.keys()
            next_sequence = 1
            if 'template_ids' in context_keys:
                if len(self.env.context.get('template_ids')) > 0:
                    next_sequence = len(self.env.context.get('template_ids')) + 1
        res.update({'mail_sequence': next_sequence, 'time_to_send':"00:00"})
        return res

    mail_sequence = fields.Integer("Sequence", default=1)
    template_id = fields.Many2one('mail.template', 'E Mail Template')
    delay_days = fields.Integer('Delay Days')  # for getting a number to send mail on the particular number
    time_to_send = fields.Char('Time To Send', default="00:00")
    send_now = fields.Boolean("Send Immediately", default=False)
    template_tag_id = fields.Many2one('crm.campaign', 'E Mail Template')

    @api.onchange('send_now')
    def onchange_send_now(self):
        if self.send_now == True:
            self.delay_days = 0
            self.time_to_send = "00:00"


class crm_tracking_campaign(models.Model):
    _name = "crm.campaign"
    _description = "CRM Campaign"

    name = fields.Char("Campaign Name", required=True)
    model_id = fields.Many2one("ir.model", "Campaign Applies to")
    model_id_2 = fields.Many2one("ir.model", "Campaign Applies to")
    model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    model_change = fields.Boolean("Model Changed", default=False)
    email_template_ids = fields.One2many('campaign.mail.template', 'template_tag_id', string="Mail Templates")
    no_delete = fields.Boolean("Can be deleted?", default=False)

    # onchange function to make the model_id as readonly
    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            self.model_id_2 = self.model_id.id
            self.model_change = True

    @api.model
    def create(self, vals):
        if vals.get('model_id_2'):
            vals['model_id'] = vals.get('model_id_2')
        if vals.get('email_template_ids'):
            for line in vals.get('email_template_ids'):
                if line[2]:
                    if line[2].get('mail_sequence') == 1 and line[2].get('delay_days') == 0 and line[2].get('send_now') == False:
                        raise UserError(_('If send now option is not selected you must give send mail time and delay days for the first line.'))

                    if line[2].get('mail_sequence') > 1 and line[2].get('delay_days') == 0:
                        raise UserError(_('You must enter delay days except for the first line'))

                    send_time = line[2].get('time_to_send')
                    if send_time == None:
                        send_time = '00:00'
                        try:
                            time.strptime(send_time, '%H:%M')
                        except:
                            raise exceptions.except_orm(_('Invalid Time format in Time to Send, should be(HH:MM)'))
        return super(crm_tracking_campaign, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('model_id_2'):
            vals['model_id'] = vals.get('model_id_2')
        res = super(crm_tracking_campaign, self).write(vals)
        if vals.get('email_template_ids'):
            for line in self.email_template_ids:
                if line.mail_sequence == 1 and line.delay_days == 0 and line.send_now == False:
                    raise UserError(_('If send now option is not selected you must give send mail time and delay days for the first line.'))

                if line.mail_sequence > 1 and line.delay_days == 0:
                    raise UserError(_('You must enter delay days except for the first line'))

                if line.time_to_send:
                    send_time = line.time_to_send
                    try:
                        time.strptime(send_time, '%H:%M')
                    except:
                        raise exceptions.except_orm(_('Invalid Time format in Time to Send, should be(HH:MM)'))
        return res

    # to prevent the default campaigns being deleted
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.no_delete == True:
                raise UserError(_('Default Campaign(s) cannot be deleted. You can only customize it.'))
        return super(crm_tracking_campaign, self).unlink()

    # to duplicate the record
    @api.one
    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {}, no_delete=False, name=_("%s (Copy)") % self.name)
        return super(crm_tracking_campaign, self).copy(default=default)

    # mail scheduler
    @api.multi
    def send_mail_scheduler(self):
        # finding the scheduler start and end time for every 15 minutes
        user_pool = self.env['res.users'].browse(SUPERUSER_ID)
        timez = user_pool.tz
        if not timez:
            raise UserError(_('Timezone is not given for the user'))
        time_ist =datetime.now(timezone(timez))
        new_time = (time_ist.strftime('%Y-%m-%d %H:%M:%S'))
        time_now =(time_ist.strftime("'%Y-%m-%d %H:%M:%S'"))
        cron_start_time = datetime.now().strptime(time_now, "'%Y-%m-%d %H:%M:%S'")

        
        datetime_object = datetime.strptime(new_time, '%Y-%m-%d %H:%M:%S')        
        from_now_15mns = datetime_object + timedelta(minutes=15)
        added_time = datetime.strftime(from_now_15mns, "'%Y-%m-%d %H:%M:%S'")
        cron_end_time = datetime.now().strptime(added_time, "'%Y-%m-%d %H:%M:%S'")
        

        # searching for the active customers
        partner_sr = self.env["res.partner"].search([('active', '=', True), ('opt_out', '=', False), ('followup_line_ids', '!=', False)])
        for partner in partner_sr:
            if partner.email:
                if partner.followup_line_ids:
                    for line in partner.followup_line_ids:
                        datetime_obt = datetime.strptime(line.next_mail_date, '%Y-%m-%d %H:%M:%S')
                        if partner_sr.tz:
                            new_date_partner = datetime_obt.replace(tzinfo=timezone(partner_sr.tz))+ timedelta(hours=5,minutes=30)
                        else:
                            raise UserError(_('Timezone is not given for the customer'))
                        next_mails_date =(new_date_partner.strftime('%Y-%m-%d %H:%M:%S'))
                        
                        if not line.next_template_id and not next_mails_date:
                            continue
                        mailing_time = datetime.strptime(next_mails_date, '%Y-%m-%d %H:%M:%S')
                        if cron_start_time <= mailing_time and cron_end_time >= mailing_time:
                            template_id = line.next_template_id
                            template_id.send_mail(partner.id, force_send=True, raise_exception=True)
                            # for finding the next template and the next mailing datetime
                            cur_mail_seq = line.mail_seq
                            next_templates = self.env['campaign.mail.template'].search([('template_tag_id', '=', line.crm_campaign_id.id), ('mail_sequence', '>', cur_mail_seq)])
                            if next_templates:
                                for tag in next_templates:
                                    # conversion of time to UTC
                                    tz = partner.tz
                                    final_utc_date = self.env["time.conversion"].time_conversion(tag.delay_days, tag.time_to_send, tz)
                                    next_mail_date = final_utc_date
                                    partner.followup_line_ids.write({'next_template_id': tag.template_id.id, 'next_mail_date': next_mail_date, 'mail_seq':tag.mail_sequence})

        crm_lead = self.env["crm.lead"].search([('opt_out', '=', False), ('lead_followup_line_ids', '!=', False)])
        for lead in crm_lead:
            if lead:
                if lead.lead_followup_line_ids:
                    for line in lead.lead_followup_line_ids:
                        datetime_obt = datetime.strptime(line.next_mail_date, '%Y-%m-%d %H:%M:%S')
                        new_date = datetime_obt.replace(tzinfo=timezone(timez))+ timedelta(hours=5,minutes=30) 
                        next_mail_date =(new_date.strftime('%Y-%m-%d %H:%M:%S'))

                        if not line.next_template_id and not next_mail_date:
                            continue
                        mailing_time = datetime.strptime(next_mail_date, '%Y-%m-%d %H:%M:%S')
                        if cron_start_time <= mailing_time and cron_end_time >= mailing_time:
                            template_id = line.next_template_id  # Get the template id and send the mail
                            template_id.send_mail(lead.id, force_send=True, raise_exception=True)
                            cur_mail_seq = line.mail_seq
                           
                            next_templates = self.env['campaign.mail.template'].search([('template_tag_id', '=', line.crm_campaign_id.id), ('mail_sequence', '>', cur_mail_seq)])
                            if next_templates:
                                for tag in next_templates:
                                    # datetime conversion to UTC
                                    if lead.partner_id:
                                        tz = lead.partner_id.tz
                                    else:
                                        user_pool = self.env['res.users'].browse(SUPERUSER_ID)
                                        tz = str(pytz.timezone(user_pool.partner_id.tz) or pytz.utc)

                                    final_utc_date = self.env["time.conversion"].time_conversion(tag.delay_days, tag.time_to_send, tz)
                                    next_mail_date = final_utc_date
                                    lead.lead_followup_line_ids.write({'next_template_id': tag.template_id.id, 'next_mail_date': next_mail_date, 'mail_seq':tag.mail_sequence})
        return True
