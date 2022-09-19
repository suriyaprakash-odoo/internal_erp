# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CrmLeadCampaign(models.TransientModel):
    _name = 'partner.campaign'
    _description = 'Assign Lead Campaign'

    crm_campaign_id = fields.Many2one('crm.campaign', 'Campaign')

    @api.multi
    def action_set_campaigns(self):

        partners = self.env['res.partner'].browse(self.env['res.partner']._context.get('active_ids'))
#         partners = self.env['res.partner'].browse(self.env.context.get('active_ids'))
        for partner in partners:
            find_campaign = partner.followup_line_ids.filtered(lambda s: s.crm_campaign_id.id == self.crm_campaign_id.id)
            if not find_campaign:
                partner.write({'followup_line_ids': [(0, 0, {'crm_campaign_id': self.crm_campaign_id.id})]})
        return True
