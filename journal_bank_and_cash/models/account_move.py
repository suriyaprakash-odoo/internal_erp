from odoo import api, fields, models,_

class AccountMove(models.Model):
    _inherit = "account.move"
    _description = "Account Entry"
    
    inv_type = fields.Selection([
            ('sale', 'Sale'),
            ('purchase', 'Purchase'),
            ('cash', 'Cash'),
            ('bank', 'Bank'),
            ('general', 'Miscellaneous'),
        ],
        help="Select 'Sale' for customer invoices journals.\n"\
        "Select 'Purchase' for vendor bills journals.\n"\
        "Select 'Cash' or 'Bank' for journals that are used in customer or vendor payments.\n"\
        "Select 'General' for miscellaneous operations journals.")
    
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, states={'posted': [('readonly', True)]},default=False)
    
    
    @api.onchange('inv_type')
    def onchange_type(self):
        res = {}
        if self.inv_type:
            res['domain'] = {'journal_id': [('type', '=', self.inv_type)]}
#             res['default'] = {'journal_id':False}
        else:
            res['domain'] = False
#             res['default'] = {'journal_id':False}
        return res