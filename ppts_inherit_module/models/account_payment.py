# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    
    _inherit = "account.payment"

    check_number = fields.Char(string="Check Number", copy=False,
        help="The selected journal is configured to print check numbers. If your pre-printed check paper already has numbers "
             "or if the current numbering is wrong, you can change it in the journal configuration page.")
    
class AccountJournal(models.Model):
    _inherit = "account.journal"
    
    @api.one
    @api.constrains('currency_id', 'default_credit_account_id', 'default_debit_account_id')
    def _check_currency(self):
        if self.currency_id:
            if self.default_credit_account_id and not self.default_credit_account_id.currency_id.id == self.currency_id.id:
                raise ValidationError(_('Configuration error!\nThe currency of the journal should be the same than the default credit account.'))
            if self.default_debit_account_id and not self.default_debit_account_id.currency_id.id == self.currency_id.id:
                raise ValidationError(_('Configuration error!\nThe currency of the journal should be the same than the default debit account.'))


    