from odoo import fields, models


class CrmIndustry(models.Model):
    
    _name = 'crm.industry'
    _description = 'Crm Industry'
    
    name = fields.Char(string='Name', required=True)
    

class CrmServices(models.Model):
    
    _name = 'crm.services'
    _description = 'Crm Services'
    
    name = fields.Char(string='Name', required=True)