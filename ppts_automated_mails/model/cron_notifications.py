from odoo import fields, models, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class Employee(models.Model):
    _inherit = "hr.employee"


    def tenure_notification_cron(self):
        employee_id = self.env['hr.employee'].search([])
        for rec in employee_id:
            if rec.doj:
                fmt = '%Y-%m-%d'
                doj = datetime.strptime(rec.doj, fmt)
                date_now = str(datetime.now().date())

                template_id = self.env.ref('ppts_automated_mails.tenure_notification_email').id
                mail_template = self.env['mail.template'].browse(template_id)

                if rec.doj[8:10] == date_now[8:10] and rec.doj[5:7] == date_now[5:7]:

                	total_tenure = int(date_now[:4])- int(rec.doj[:4])

                	if mail_template:
                		mail_template.with_context(total_tenure=total_tenure).send_mail(rec.id, force_send=True)


    def birthday_notification_cron(self):
        employee_id = self.env['hr.employee'].search([])
        for rec in employee_id:
            if rec.birthday:
                fmt = '%Y-%m-%d'
                birthday = datetime.strptime(rec.birthday, fmt)
                date_now = str(datetime.now().date())

                template_id = self.env.ref('ppts_automated_mails.birthday_notification_email').id
                mail_template = self.env['mail.template'].browse(template_id)

                if rec.birthday[8:10] == date_now[8:10] and rec.birthday[5:7] == date_now[5:7]:

                	if mail_template:
                		mail_template.send_mail(rec.id, force_send=True)


    def anniversary_notification_cron(self):
        employee_id = self.env['hr.employee'].search([])
        for rec in employee_id:
            if rec.date_of_marriage:
                fmt = '%Y-%m-%d'
                date_of_marriage = datetime.strptime(rec.date_of_marriage, fmt)
                date_now = str(datetime.now().date())

                template_id = self.env.ref('ppts_automated_mails.anniversary_notification_email').id
                mail_template = self.env['mail.template'].browse(template_id)

                if rec.date_of_marriage[8:10] == date_now[8:10] and rec.date_of_marriage[5:7] == date_now[5:7]:

                    if mail_template:
                        mail_template.send_mail(rec.id, force_send=True)


    def probation_completion_notification_cron(self):
        employee_id = self.env['hr.employee'].search([])
        for rec in employee_id:
            if rec.contract_id:
                if rec.contract_id.trial_date_end:
                    fmt = '%Y-%m-%d'
                    date_of_marriage = datetime.strptime(rec.contract_id.trial_date_end, fmt)
                    date_now = str(datetime.now().date())

                    template_id = self.env.ref('ppts_automated_mails.anniversary_notification_email').id
                    mail_template = self.env['mail.template'].browse(template_id)

                    if rec.contract_id.trial_date_end[8:10] == date_now[8:10] and rec.contract_id.trial_date_end[5:7] == date_now[5:7]:

                        if mail_template:
                            mail_template.send_mail(rec.id, force_send=True)