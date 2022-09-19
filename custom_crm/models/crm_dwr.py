from odoo import fields, models, api
from datetime import datetime


class DwrCrm(models.Model):
    _name = "crm.dwr"
    _description = 'Crm Report'
    
    @api.onchange('name')
    def count_of_lead(self):
        tele = [];odoo = [];pre_sale = [];other = [];web = [];total = [];row = [];partner = ""
        crm_id = self.env['crm.lead'].search([])
        for rec in crm_id:
            if rec.create_date:
                date = str(datetime.strptime(rec.create_date, '%Y-%m-%d %H:%M:%S').date())
                if date == self.name:
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
        self.odoo_lead = len(odoo)
        self.telesales_lead = len(tele)
        self.presales_lead = len(pre_sale)
        self.any_other_sources_lead = len(other)
        self.website_lead = len(web)
        
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
                self.dwr_success = str(count) + ' - (' + partner + ')'
            else:
                self.dwr_success = str(count)      
        else:
            self.dwr_success = ''
    
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    name = fields.Date(default=datetime.today(), readonly=True)
    dwr_success = fields.Char()
    dwr_setback = fields.Char()
    training_activity = fields.Text()
    review_activity = fields.Text()
    key_observation = fields.Text()
    other_details = fields.Text()
    odoo_lead = fields.Char("Odoo")
    telesales_lead = fields.Char("Telesales")
    presales_lead = fields.Char("Presales")
    any_other_sources_lead = fields.Char("Any Other Sources")
    website_lead = fields.Char("Website")
    odoo_demo = fields.Integer("Odoo")
    telesales_demo = fields.Integer("Telesales")
    presales_demo = fields.Integer("Presales")
    any_other_sources_demo = fields.Integer("Any Other Sources")
    no_show_demo = fields.Integer("No show")
    client_state_ids = fields.One2many('crm.dwr.state', 'crm_dwr_id')

    def report_mail(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('custom_crm', 'crm_dwr_mail_template')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            'default_model': 'crm.dwr',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
                                        
                                        
class DwrCrmState(models.Model):
    _name = "crm.dwr.state"
    _description = 'Crm Report Details'
    
    client_name_id = fields.Many2one('res.partner', 'Client Name', required=True)
    area = fields.Char("Area")
    value = fields.Char("Value")
    details = fields.Char("Details")
    crm_dwr_id = fields.Many2one('crm.dwr')
        
