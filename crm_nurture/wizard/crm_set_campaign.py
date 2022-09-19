# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLeadCampaign(models.TransientModel):
    _name = 'crm.lead.campaign'
    _description = 'Assign Lead Campaign'

    crm_campaign_id = fields.Many2one('crm.campaign', 'Campaign')

    @api.multi
    def action_set_campaigns(self):

        leads = self.env['crm.lead'].browse(self.env.context.get('active_ids'))
        for lead in  leads:
            find_campaign = lead.lead_followup_line_ids.filtered(lambda s: s.crm_campaign_id.id == self.crm_campaign_id.id)
            if not find_campaign:
                lead.write({'lead_followup_line_ids': [(0, 0, {'crm_campaign_id': self.crm_campaign_id.id})]})
        return True
