# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import date

class AccountTdsRate(models.TransientModel):
    _name = 'account.tds.rate'
    _description = 'Account TDS Rate Update'
    
    date_from = fields.Date('Date Applicable From', required=True, default=date.today())
    tds_percentage = fields.Float('TDS Rate', required=True)
    tds_exempt_limit = fields.Float('TDS Threshold Limit', required=True)
    sur_percentage = fields.Float('Sur Rate', required=True)
    sur_exempt_limit = fields.Float('Sur Exempt Limit', required=True)
    
    @api.multi
    def Done(self):
        context = dict(self.env.context or {})
        act_id = context.get('act_id', False)
        tds_id = self.env['account.tds'].search([('id', '=', act_id)])
        if tds_id:
            tds_id.write({
                'tds_percentage': self.tds_percentage,
                'tds_exempt_limit': self.tds_exempt_limit,
                'sur_percentage': self.sur_percentage,
                'sur_exempt_limit': self.sur_exempt_limit
                })
            tds_line_ids = self.env['account.tds.line'].create({
                'tds_id': tds_id.id,
                'active_line':True,
                'date_from': self.date_from,
                'tds_percentage': self.tds_percentage,
                'tds_exempt_limit': self.tds_exempt_limit,
                'sur_percentage': self.sur_percentage,
                'sur_exempt_limit': self.sur_exempt_limit
            })
            tds_line_ids = self.env['account.tds.line'].search([('id', '!=', tds_line_ids.id),('tds_id', '=', tds_id.id)])
            for line in tds_line_ids:
                line.active_line = False
        return {'type': 'ir.actions.act_window_close'}
