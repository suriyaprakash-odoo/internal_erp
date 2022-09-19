from odoo import api, fields, models, _
from odoo.exceptions import Warning



class HrHolidaysPublicLine(models.Model):
    _inherit = 'hr.holidays.public.line'
    
    
    holiday_type = fields.Selection(string='Type',
        selection=[('public_hoildays', 'Public Holidays'), ('week_off', 'Week Off'), ('others', 'Others')])


