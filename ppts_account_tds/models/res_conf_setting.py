# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    payment_journal_id = fields.Many2one('account.journal', string='Payment Journal', 
                            related='company_id.payment_journal_id', domain=[('type', '=', 'bank')])
 
class ResCompany(models.Model):
    _inherit = 'res.company'

    payment_journal_id = fields.Many2one('account.journal')
    