from odoo import api, fields, models, _

class EmailTemplate(models.Model):
    _inherit = "mail.template"

    auto_delete = fields.Boolean("Auto Delete", default=False)
    unsubscribe_link = fields.Char("Unsubscribe Link")

    def build_expression(self, field_name, sub_field_name, null_value):
        expression = ''
        if field_name:
            expression = "${object." + field_name
            if sub_field_name:
                expression += "." + sub_field_name
            if null_value:
                expression += " or '''%s'''" % null_value
            expression += " or ''}"
        return expression

    @api.onchange('model_id')
    def onchange_model_id(self):
        if self.model_id:
            if self.model_id.model=="res.partner":
                self.email_to ="${object.email}"
                self.partner_to = "${object.id}"
                self.unsubscribe_link = '<a href="/Unsubscribe?obj_id=${object.id}&amp;model=res.partner">Unsubscribe</a>'
            if self.model_id.model=="crm.lead":
                self.email_to ="${object.email_from}"
                self.partner_to =''
                self.unsubscribe_link = '<a href="/Unsubscribe?obj_id=${object.id}&amp;model=crm.lead">Unsubscribe</a>'
