# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models

class Employee(models.Model):
    _inherit = 'hr.employee'
    
    is_esi = fields.Boolean("ESI", default=False)
    is_pf = fields.Boolean("PF", default=False)
    employee_type = fields.Selection([('existing','Existing Employee'),('new','New Employee')])
    
    
class Contract(models.Model):
    _inherit = "hr.contract"
    
    employee_type = fields.Selection([('existing','Existing Employee'),('new','New Employee')])
    
    @api.onchange('employee_id')
    def onchage_employee_type(self):
        self.employee_type = self.employee_id.employee_type
    

class ContractRule(models.Model):
    _inherit = "hr.contract.rule"
      
    employee_type = fields.Selection([('existing','Existing Employee'),('new','New Employee')])
     
