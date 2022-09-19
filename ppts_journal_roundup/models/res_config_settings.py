# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    roundup_account_id = fields.Many2one("account.account", 
            related='company_id.roundup_account_id', string='Round Off Account')
    roundoff_label = fields.Char("Label", related='company_id.roundoff_label')
