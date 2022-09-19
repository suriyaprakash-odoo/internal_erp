from odoo import api, fields, models


class assign_followers_settings(models.Model):
    _name = 'assign.followers.settings'
    _description = 'Settings for Assign and Remove followers to a Record'

    name = fields.Char(string='Name', required=True)
    crm_team = fields.Many2one('mail.channel', string="Channel", copy=False)
    model_id = fields.Many2one('ir.model', 'Model')
    is_check = fields.Boolean('check', default=False, copy=False)
    
    @api.multi
    def create_action(self,id):
        crm_lead = self.env['crm.lead'].search([('id','=',id)])
        mail_follow_id = self.env['mail.followers']
        for wizard in self:
            new_channels = wizard.crm_team
        for crm in crm_lead:
            if self.crm_team:
                if not mail_follow_id.search([('res_model', '=', self.model_id.model), ('res_id', '=', crm.id), ('channel_id', '=', self.crm_team.id)]):
                    crm.message_subscribe([],new_channels.ids)
                    self.is_check = True
              
