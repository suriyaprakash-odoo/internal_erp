# -*- coding: utf-8 -*-

from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"
    
#     @api.depends("line_ids")
#     def roundup_CRDR_amount(self):
#         for rec in self:
#             for line_id in rec.line_ids:
# #                 print(line_id.debit, line_id.credit, "Before")
#                 line_id.debit, line_id.credit = round(line_id.debit), round(line_id.credit)
# #                 print(line_id.debit, line_id.credit, "After")
                
                
#     @api.multi
#     def assert_balanced(self):
#         if not self.ids:
#             return True
#         prec = self.env['decimal.precision'].precision_get('Account')

#         self._cr.execute("""\
#             SELECT      move_id
#             FROM        account_move_line
#             WHERE       move_id in %s
#             GROUP BY    move_id
#             HAVING      abs(sum(debit) - sum(credit)) > %s
#             """, (tuple(self.ids), 10 ** (-max(5, prec))))
# #         print(len(self._cr.fetchall()))
# #         if len(self._cr.fetchall()) != 0:
# #             raise UserError(_("Cannot create unbalanced journal entry."))
#         return True
    
    @api.model
    def create(self, vals):
        _logger.warning("--", vals)
        move_id = super(AccountMove, self).create(vals)
        # if move_id.journal_id.round_up:
        #     move_id.roundup_CRDR_amount()
        return move_id
     
     
#     @api.multi
#     def write(self, vals):
#         move_id = super(AccountMove, self).create(vals)
# #         if self.journal_id.round_up:
#         self.roundup_CRDR_amount()
#         return move_id
        
        

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model
    def create(self, vals):
        _logger.warning("--", vals['credit'], '--', vals['debit'])
        move_id = super(AccountMoveLine, self).create(vals)
        return move_id