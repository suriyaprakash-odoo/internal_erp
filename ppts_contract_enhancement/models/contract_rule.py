
from odoo import fields, models, api, _
from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta


class HrContractRule(models.Model):
    _name = 'hr.contract.rule'
    
    name = fields.Char(string="Name", required=True)
    from_amount = fields.Float(string="From Amount")
    to_amount = fields.Float(string="To Amount")
    basic = fields.Float(string="Basic")
    basic_method = fields.Selection([('percent','Percentage'),('fixed','Fixed')], string="Method", default="percent")
    hra = fields.Float(string="HRA")
    hra_method = fields.Selection([('percent','Percentage'),('fixed','Fixed')], string="Method", default="percent")
    transport = fields.Float(string="Transport")
    transport_method = fields.Selection([('percent','Percentage'),('fixed','Fixed')], string="Method", default="percent")
    medical = fields.Float(string="MA")
    medical_method = fields.Selection([('percent','Percentage'),('fixed','Fixed')], string="Method", default="percent")
    project = fields.Float(string="Project Allowance")
    project_method = fields.Selection([('percent','Percentage'),('fixed','Fixed')], string="Method", default="percent")
    exgratia = fields.Float(string="Exgratia")
    exgratia_method = fields.Selection([('percent','Percentage'),('fixed','Fixed')], string="Method", default="percent")
