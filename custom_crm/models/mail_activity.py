from odoo import fields, models
from datetime import datetime
    
    
class MailActivity(models.Model):
    _inherit = 'mail.activity'
    
    def _get_crm_lead(self):
        for rec in self:
            crm_id = self.env['crm.lead'].search([('id', '=', rec.res_id), ('name', '=', rec.res_name)])
            if crm_id:
                rec.crm_lead_id = crm_id.id
                
    def _get_date_cal(self):
        for rec in self:
            fmt = '%Y-%m-%d'
            last_active = datetime.strptime(rec.date_deadline, fmt)
            time_now = datetime.today()
            rec.date_diff = str((time_now - last_active).days + 1)
    
    res_name = fields.Char('Document Name', compute='_compute_res_name', store=True,help="Display name of the related document.", readonly=True, copy=False)
    crm_lead_id = fields.Many2one('crm.lead', string="Opportunity", compute='_get_crm_lead', copy=False)
    last_action = fields.Boolean('last Activity', default=False)
    date_diff = fields.Char(string='Date Different', compute='_get_date_cal', copy=False, default='0')


