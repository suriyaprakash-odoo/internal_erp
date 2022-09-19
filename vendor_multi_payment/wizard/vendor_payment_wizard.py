# -*- coding: utf-8 -*-

from odoo import fields, models, api


class AccountTdsRate(models.TransientModel):
    _name = 'vendor.multi.payment.wizard'
    _description = 'Challan number Update'
    
    challan_no = fields.Char(string='Challan No.')
    
    @api.multi
    def Done(self):
        context = dict(self.env.context or {})
        act_id = context.get('act_id', False)
        multi_id = self.env['vendor.multi.payment'].search([('id', '=', act_id)])
        if multi_id:
            multi_id.write({
                'challan_no': self.challan_no,
                })
            multi_id.account_move_id.write({
                'challan_no': multi_id.challan_no,
                })
        return {'type': 'ir.actions.act_window_close'}
