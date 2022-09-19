from odoo import api, fields, models, _
from odoo.exceptions import UserError
import re

class EmailFollowupLine(models.Model):
    _inherit = "email.followup.line"

    lead_id = fields.Many2one("crm.lead",string="Lead/Opportunity")

class Lead(models.Model):
    _inherit = "crm.lead"

    lead_followup_line_ids = fields.One2many("email.followup.line", "lead_id", string="Followup Line")
    total_mails = fields.Integer(compute='_compute_tracking_lead_counts', string='Total Mails')
    sent_ratio = fields.Integer(compute='_compute_tracking_lead_counts', string='Sent Mails')
    opened_ratio = fields.Integer(compute='_compute_tracking_lead_counts', string='Opened')
    error_ratio = fields.Integer(compute='_compute_tracking_lead_counts', string='Error')
    bounced_ratio = fields.Integer(compute='_compute_tracking_lead_counts', string='Bounced')

    @api.multi
    def validate_email(self,email):
        if email:
            match= re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,5}|[0-9]{1,3})(\\]?)$", email)
        return match

    @api.model
    def create(self, vals):
        if vals.get('email_from'):
            email = vals.get('email_from')
            validate_email = self.validate_email(email)
            if validate_email == None:
                raise UserError(_('Please enter a valid Email Address'))
        return super(Lead,self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('email_from'):
            email = vals.get('email_from')
            validate_email = self.validate_email(email)
            if validate_email == None:
                raise UserError(_('Please enter a valid Email Address'))
        return super(Lead, self).write(vals)

    def _compute_tracking_lead_counts(self):
        for lead in self:

            if lead.lead_followup_line_ids:
                lead.total_mails = self.env['mail.tracking.email'].search_count([('lead_id', '=', lead.id)])
                lead.sent_ratio = self.env['mail.tracking.email'].search_count([('lead_id', '=', lead.id), ('state', '=', 'sent')])
                lead.opened_ratio = self.env['mail.tracking.email'].search_count([('lead_id', '=', lead.id), ('state', '=', 'opened')])
                lead.error_ratio = self.env['mail.tracking.email'].search_count([('lead_id', '=', lead.id), ('state', '=', 'error')])
                lead.bounced_ratio = self.env['mail.tracking.email'].search_count([('lead_id', '=', lead.id), ('state', '=', 'bounced')])

                
    @api.multi
    def call_wizard_lead(self):
        wizard_form = self.env.ref('crm_nurture.crm_set_campaign_form', False)
        return {
                    'name'      : _('Set Campaign'),
                    'type'      : 'ir.actions.act_window',
                    'res_model' : 'crm.lead.campaign',
                    'view_id'   : wizard_form.id,
                    'view_type' : 'form',
                    'view_mode' : 'form',
                    'target'    : 'new',
                    'context'   : {'active_ids':self.env.context.get('active_ids')}
                }
            



class Lead2Opportunity(models.TransientModel):
    _inherit = "crm.lead2opportunity.partner"

    campaign_action = fields.Selection(
        [
            ('none', 'None'),
            ('do_not_delete', 'Do not Delete the Existing Campaigns'),
            ('delete_all', 'Delete All the Existing Campaigns'),
        ], 'Campaign Action', required=True,default="none",
            help="*Option 1: This will not delete any campaign mapped with the current lead,\
             the existing campaigns will continue in the Opportunity stage. \
             You can add campaigns additionally if needed. \n *Option 2: Deletes all the existing campaigns mapped with the current lead.\
             You can add new campaigns in Opportunity Stage")

    @api.multi
    def action_apply(self):
        if self.campaign_action == "none":
            raise UserError(_("Please select any one of the following action item for the Campaigns \n"
                              "\t 1. Do not Delete the Existing Campaigns \n"
                              "\t 2. Delete All the Existing Campaigns"))
        if self.campaign_action =="delete_all":
            leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
            for lead in leads:
                lead.lead_followup_line_ids.unlink()
        return super(Lead2Opportunity,self).action_apply()

class Lead2OpportunityMassConvert(models.TransientModel):
    _inherit = 'crm.lead2opportunity.partner.mass'

    @api.multi
    def mass_convert(self):
        if self.campaign_action == "none":
            raise UserError(_("Please select an action item for the campaigns \n"
                              "\t 1. Do not Delete the Existing Campaigns \n"
                              "\t 2. Delete All the Existing Campaigns"))

        if self.campaign_action =="delete_all":
            leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
            for lead in leads:
                lead.lead_followup_line_ids.unlink()
        return super(Lead2OpportunityMassConvert,self).mass_convert()