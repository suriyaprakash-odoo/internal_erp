# -*- coding: utf-8 -*-


from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from odoo.exceptions import UserError


class ResCompany(models.Model):
    _inherit = "res.company"

    roundup_account_id = fields.Many2one("account.account", string='Round Up Account')
    roundoff_label = fields.Char("Label")
