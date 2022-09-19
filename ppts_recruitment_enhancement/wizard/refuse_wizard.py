# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from odoo import api, fields, models, _

class RefuseUpdate(models.TransientModel):
    """
    This wizard is used to cancel reason update
    """
    _name = 'refuse.reason.update'
    _description = 'Update Cancel Reason'

    name = fields.Char(string='Reason for Cancel')
    

    @api.multi
    def update_refuse_reason(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids')
        hr_job_ids = self.env['hr.job'].search([('id', '=' , active_ids)])
        if hr_job_ids:
            hr_job_ids.reason_for_cancel = self.name
            hr_job_ids.state = 'refuse'
        
