# See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    over_credit = fields.Boolean('Allow Over Credit?')
    code = fields.Char("Code",size=5)
    customer_type_id = fields.Many2one('ppts.customer.type.master',"Customer Type")
    
    gst_no = fields.Char("GST No")
    division = fields.Char("Division")
    range_val = fields.Char("Range")
    pan_no = fields.Char("PAN No.")
    service_tax_no = fields.Char("Service Tax No")
    partner_name = fields.Char("First name",index=True,required=True)

    name = fields.Char(
        compute="_compute_name",
        # inverse="_inverse_name_after_cleaning_whitespace",
        required=False,readonly=False,
        store=True)

    @api.model
    def _get_computed_name(self, partner_name, code):
        """Compute the 'name' field according to splitted data.
        You can override this method to change the order of partner_name and
        code the computed name"""
        # order = self._get_names_order()
        return " ".join((p for p in (code, partner_name) if p))
        

    @api.multi
    @api.depends("name", "code")
    def _compute_name(self):
        """Write the 'name' field according to splitted data."""
        for record in self:
            record.name = record._get_computed_name(
                record.partner_name, record.code,
            )

    @api.onchange('partner_name')
    def onchange_partner_name(self):
        if self.partner_name:
            self.name = self.partner_name
        else:
            self.name = ''

    # @api.multi
    # @api.depends('name', 'code')
    # def name_get(self):
    #     result = []
    #     for item in self:
    #         if item.code:
    #             name = item.code + "-" + item.name
    #         else:
    #             name = item.name
                
    #         result.append((item.id, name))
    #     return result