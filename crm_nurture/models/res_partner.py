from odoo import api, fields, models, _
import re
from odoo.exceptions import UserError

class EmailFollowupLine(models.Model):
    _inherit = "email.followup.line"

    partner_id = fields.Many2one("res.partner",string="Partner")

class ResPartner(models.Model):
    _inherit = "res.partner"

    followup_line_ids = fields.One2many("email.followup.line","partner_id", string="Followup Line")
    total_mails = fields.Integer(compute='_compute_tracking_counts', string='Total Mails')
    sent_ratio = fields.Integer(compute='_compute_tracking_counts', string='Sent Mails')
    opened_ratio = fields.Integer(compute='_compute_tracking_counts', string='Opened')
    error_ratio = fields.Integer(compute='_compute_tracking_counts', string='Error')
    bounced_ratio = fields.Integer(compute='_compute_tracking_counts',string='Bounced')

    @api.multi
    def validate_email(self, email):
        if email:
            match = re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,5}|[0-9]{1,3})(\\]?)$", email)
        return match

    @api.model
    def create(self, vals):
        if vals.get('email'):
            email = vals.get('email')
            validate_email = self.validate_email(email)
            if validate_email == None:
                raise UserError(_('Please enter a valid Email Address'))
        return super(ResPartner, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('email'):
            email = vals.get('email')
            validate_email = self.validate_email(email)
            if validate_email == None:
                raise UserError(_('Please enter a valid Email Address'))
        return super(ResPartner, self).write(vals)

    def _compute_tracking_counts(self):
        for partner in self:

            if partner.followup_line_ids:
                partner.total_mails = self.env['mail.tracking.email'].search_count([('partner_id', '=', partner.id)])
                partner.sent_ratio = self.env['mail.tracking.email'].search_count([('partner_id', '=', partner.id),('state', '=', 'sent')])
                partner.opened_ratio = self.env['mail.tracking.email'].search_count([('partner_id', '=', partner.id), ('state', '=', 'opened')])
                partner.error_ratio = self.env['mail.tracking.email'].search_count([('partner_id', '=', partner.id), ('state', '=', 'error')])
                partner.bounced_ratio = self.env['mail.tracking.email'].search_count([('partner_id', '=', partner.id), ('state', '=', 'bounced')])
                
    @api.multi
    def call_wizard_customer(self):
        wizard_form = self.env.ref('crm_nurture.partner_set_campaign_form', False)
        return {
                    'name'      : _('Set Campaign'),
                    'type'      : 'ir.actions.act_window',
                    'res_model' : 'partner.campaign',
#                     'res_id'    : new.id,
                    'view_id'   : wizard_form.id,
                    'view_type' : 'form',
                    'view_mode' : 'form',
                    'target'    : 'new',
                    'context'   : {'active_ids':self.env.context.get('active_ids')}
                }
            