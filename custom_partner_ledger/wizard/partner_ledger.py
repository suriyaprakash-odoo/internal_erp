from odoo import models, fields, api,_


class PartnerLedger(models.TransientModel):
    _name = "partner.ledger.report"

    all_partners = fields.Boolean("All Partners",default=True,help="Show the ledger for all partners \n If unchecked you can choose one or multiple partners to show the ledgers  ")
    partner_ids = fields.Many2many('res.partner',string="Partners", help="Select the partners to show the ledgers")

    @api.onchange('all_partners')
    def onchange_all_partners(self):
        if self.all_partners:
            self.partner_ids = False

    @api.multi
    def report_partner_ledger(self):
        return {
                'type': 'ir.actions.client',
                'name': _('Partner Ledger'),
                'tag': 'account_report',
                'options': {'partner_id': self.partner_ids.ids},
                'ignore_session': 'read',
                'context': "{'model':'account.partner.ledger'}"
        }


