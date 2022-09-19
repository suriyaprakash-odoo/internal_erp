from odoo import api, fields, models, _
from datetime import date,datetime,timedelta


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'  
       
    minimum_overtime_hours = fields.Char('Minimum over time Hours')
 
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            minimum_overtime_hours=params.get_param('ppts_overtime_enhancement.minimum_overtime_hours', default=False) or False,
            )
        return res
      
    @api.multi
    def set_values(self):
        self.ensure_one()
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param("ppts_overtime_enhancement.minimum_overtime_hours", self.minimum_overtime_hours)        
     
      




class Employee(models.Model):
    _inherit = "hr.employee"
    
    over_time_hours = fields.Boolean(string='Over Time')
    
    
    
    


