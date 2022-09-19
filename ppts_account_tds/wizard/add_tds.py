# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class TdsAddReconcile(models.TransientModel):
    _name = "tds.add.reconcile"
    _description = "Add the Reconcile Amount"

    tds_reconcile_method = fields.Selection([
        ('full', 'Fully Reconcile'),
        ('partial', 'Partial Reconcile'),
        ], string='How do you want to Reconcile?', default='full', required=True)

    partial_amount = fields.Float(string="Amount") 
    tds_line_id = fields.Many2one('account.tds.reconcile', string='TDS')

    @api.multi
    def add_reconcilations(self):
        accout_tds_id = self.env['account.tds.reconcile'].browse(self.tds_line_id.id)
        if self.tds_reconcile_method == 'partial':
            accout_tds_id.reconcile_amount = self.partial_amount
            accout_tds_id.add_tds()
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        else:
            accout_tds_id.add_tds()
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }

