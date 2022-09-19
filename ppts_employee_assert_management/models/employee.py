from odoo import fields, models, api, _


class Employee(models.Model):
    _inherit = "hr.employee"
    
    employee_assert_ids = fields.One2many('employee.asserts.management','employee_assert_id',string="Asserts Management")
    

class EmployeeAssertsManagement(models.Model):
    _name = "employee.asserts.management"
    
    employee_assert_id = fields.Many2one('hr.employee',string="Applicant Academic")
    name = fields.Many2one('company.asserts',string="Assert", required=True)
    unique_no = fields.Char(string="Unique Number")
    issued_by = fields.Char(string="Issued By")
    issued_at = fields.Date(string="Issued At")
    handover_to = fields.Char(string="Handover By")
    handover_at = fields.Date(string="Handover At")
    comments = fields.Text("Comments")
    issued = fields.Boolean("Issued", readonly=True)
    handover = fields.Boolean("Handed over", readonly=True)
    
    @api.onchange('issued_at','handover_at')
    def onchange_date(self):
        if self.issued_at:
            self.issued = True
        if self.handover_at:
            self.handover = True
            
#     received_date = fields.Date(String="Received Date")
#     returned_date = fields.Date(String="Returned Date")
#     remarks = fields.Char(string="Remarks")
    
class CompanyAsserts(models.Model):
    _name = "company.asserts"
    
    name = fields.Char(string="Name")
    code = fields.Char(string="Code / S.No")