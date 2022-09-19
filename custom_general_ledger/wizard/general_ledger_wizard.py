from odoo import models, fields, api,_


class GeneralLedgerReport(models.TransientModel):
    _name = "general.ledger.report"

    all_accounts = fields.Boolean("All Accounts",default=True,help="Show the ledgers for all the Chart of Accounts\n If unchecked you can choose one or multiple Chart of Accounts to show the ledger")
    account_ids = fields.Many2many('account.account',string="Accounts",help="Please select the Chart of Accounts to show the ledgers")

    @api.onchange('all_accounts')
    def onchange_all_accounts(self):
        if self.all_accounts:
            self.account_ids = False

    @api.multi
    def report_general_ledger(self):
        return {
                'type': 'ir.actions.client',
                'name': _('General Ledger'),
                'tag': 'account_report',
                'ignore_session': 'both',
                'context': "{'model':'account.general.ledger'}"
        }


