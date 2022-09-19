from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    firc_ids  = fields.Many2many("account.firc",string="FIRC Number")
    firc_count = fields.Integer(compute='_compute_firc_count',string="FIRC Number")

    @api.multi
    def _compute_firc_count(self):
        for self in self:
            if self.firc_ids:
                self.firc_count = len(self.firc_ids)

    @api.multi
    def open_related_firc(self):
        if self.firc_ids:
            return {
                'name': _('FIRC Numbers'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'account.firc',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', [x.id for x in self.firc_ids])],
            }
        else:
            raise UserError(_("FIRC Numbers are not found"))
