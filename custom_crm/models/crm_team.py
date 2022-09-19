from odoo import fields, models, api


class CrmTeam(models.Model):
    _inherit = 'crm.team'
    _rec_name = "display_name"
    
    crm_team_id = fields.Many2one('crm.team', string="Parent", copy=False)
    display_name = fields.Char('Parent', compute='_compute_display_name', store=True)
    
    @api.depends('name', 'crm_team_id')
    def _compute_display_name(self):
        for rec in self:
            if rec.crm_team_id:
                rec.display_name = '%s / %s' % (rec.crm_team_id.display_name, rec.name) 
            else:
                rec.display_name = rec.name    
    
