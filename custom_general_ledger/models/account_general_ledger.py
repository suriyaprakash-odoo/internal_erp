from odoo import models, api, _, fields

class ReportGeneralLedger(models.AbstractModel):
    _inherit = "account.general.ledger"

    @api.model
    def get_lines(self, options, line_id=None):
        account_ids = self.env["account.account"].search([('id', 'in', self._context.get('accounts'))])
        context = dict(self._context, account_ids=account_ids)
        return super(ReportGeneralLedger, self.with_context(context)).get_lines(options, line_id=line_id)