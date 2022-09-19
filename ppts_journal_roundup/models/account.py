# -*- coding: utf-8 -*-

from odoo.tools.float_utils import float_round as round
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    round_up = fields.Boolean(string="Round Off?", default=False)
    
