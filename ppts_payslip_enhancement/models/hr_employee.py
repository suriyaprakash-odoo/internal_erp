from odoo import api, fields, models, _
from odoo.exceptions import Warning
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, pycompat
import time

# hr.employee form

class Employee(models.Model):
    _inherit = "hr.employee"
    
    employee_code = fields.Char(string="Code")        
    epf_number = fields.Char(string="EPF")
    pan_number = fields.Char(string="PAN")
    uan_number = fields.Char(string="UAN")
    date_of_joining = fields.Date(string="Date of Joining")
    aadhar_number = fields.Char(string="Aadhar")
    esino = fields.Char("ESI No")


