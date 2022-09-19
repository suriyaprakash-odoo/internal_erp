from odoo import api, exceptions, fields, models, _
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning


class AccountFirc(models.Model):
    _name = "account.firc"
    _order = 'paid_date asc'

    name = fields.Char("FIRC No")
    payment_ref = fields.Char("Payment Ref")
    move_id = fields.Many2one("account.move",string="Journal Entry")
    paid_amount = fields.Float("Paid Amount")
    paid_date = fields.Date("Payment Date")